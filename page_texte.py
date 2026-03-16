import streamlit as st
import json
import html
import logging
from backend.services.texte_service import generate_texte
from backend.database.db_manager import save_to_archive
from backend.exporters.pdf_exporter import export_texte_pdf
from frontend.components.input_form import render_curriculum_form
from frontend.components.print_helper import inject_print_button
from backend.utils.rate_limit import check_rate_limit, remaining_wait
from backend.ai.suggestion_service import suggest_themes
from backend.utils.draft_manager import add_draft, render_drafts_ui
from frontend.translations import t
from backend.config import CEFR_MAP

logger = logging.getLogger(__name__)
_MAX_THEME_LEN = 200


def _do_generate(form_data: dict, theme: str, use_cache: bool = True):
    """Run text generation and store result in session_state."""
    result = generate_texte(
        niveau=form_data["niveau"],
        projet_num=form_data["projet_num"],
        sequence_num=form_data["sequence_num"],
        theme=theme,
    )
    st.session_state["current_texte"] = result
    st.session_state["last_texte_params"] = {"form_data": form_data, "theme": theme}
    add_draft("texte", result)


def render_page_texte():
    st.title(t("texte_title"))
    st.markdown(t("texte_subtitle"))


    # ── Input section ─────────────────────────────────────────────────────────
    form_data = render_curriculum_form("texte")

    # ── AI Theme Suggestions ────────────────────────────────────────────
    if form_data:
        if st.button(t("btn_suggest_theme"), use_container_width=True):
            if not check_rate_limit("suggest_theme", max_calls=10, window_sec=60):
                st.warning(t("suggest_warning"))
            else:
                with st.spinner(t("suggest_spinner")):
                    suggestions = suggest_themes(
                        niveau=form_data["niveau"],
                        projet_title=form_data["projet_title"],
                        sequence_title=form_data["sequence_title"],
                        cefr=CEFR_MAP.get(form_data["niveau"], "A1"),
                    )
                    st.session_state["texte_suggestions"] = suggestions

        # Show suggestion chips
        if "texte_suggestions" in st.session_state:
            st.caption(t("suggest_click"))
            s_cols = st.columns(3)
            for i, sug in enumerate(st.session_state["texte_suggestions"]):
                if s_cols[i].button(f"✦ {sug}", key=f"sug_texte_{i}", use_container_width=True):
                    st.session_state["texte_theme_value"] = sug
                    st.rerun()

    # ── Theme input ─────────────────────────────────────────────────────
    prefilled = st.session_state.pop("texte_theme_value", "")
    theme_raw = st.text_input(
        t("theme_specific"),
        value=prefilled,
        placeholder=t("theme_placeholder"),
        max_chars=_MAX_THEME_LEN,
    )
    theme = theme_raw.strip()

    # ── Generate / Regenerate buttons ────────────────────────────────────
    gen_col, regen_col = st.columns([2, 1])

    with gen_col:
        if st.button(t("btn_generate"), type="primary", use_container_width=True, disabled=not form_data):
            if not check_rate_limit("texte_gen"):
                st.warning(t("limit_reached", wait=remaining_wait('texte_gen')))
            else:
                with st.spinner(t("gen_spinner")):
                    try:
                        _do_generate(form_data, theme, use_cache=True)
                    except Exception as exc:
                        logger.error("Erreur génération texte: %s", exc)
                        st.error(t("gen_error"))

    with regen_col:
        has_prev = "last_texte_params" in st.session_state
        if st.button("🔁", use_container_width=True, disabled=not has_prev,
                     help=t("btn_regen_help")):
            if not check_rate_limit("texte_gen"):
                st.warning(t("limit_reached", wait=remaining_wait('texte_gen')))
            else:
                params = st.session_state["last_texte_params"]
                with st.spinner(t("regen_spinner")):
                    try:
                        _do_generate(params["form_data"], params["theme"], use_cache=False)
                        st.rerun()
                    except Exception as exc:
                        logger.error("Erreur régénération texte: %s", exc)
                        st.error(t("regen_error"))

    # Drafts UI
    render_drafts_ui("texte", "current_texte")

    # ── Output section ────────────────────────────────────────────────────────
    st.markdown("---")
    if "current_texte" in st.session_state:
        res = st.session_state["current_texte"]
        meta = res.get("_meta", {})

        st.success(f"**{res.get('titre', t('texte_title').replace('📝 ', ''))}** (Niveau: {meta.get('cefr_level', '')} - {meta.get('niveau', '')})")

        with st.container():
            safe_texte = html.escape(res.get("texte", "")).replace("\n", "<br/>")
            text_align = "right" if st.session_state.get("lang") == "ar" else "left"
            st.markdown(f"""
            <div id="cem-print-content" style="background-color: #f9f9f9; padding: 20px; border-radius: 10px;
                 border-{text_align}: 4px solid #4F8BF9; font-size: 1.1em; line-height: 1.6; text-align: {text_align};">
                {safe_texte}
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<br/>", unsafe_allow_html=True)

        with st.expander(t("vocab_title"), expanded=False):
            for v in res.get("vocabulaire_cle", []):
                st.markdown(f"- **{v.get('mot')}**: {v.get('definition')}")

        with st.expander(t("comp_questions_title"), expanded=False):
            for i, q in enumerate(res.get("questions_comprehension", []), 1):
                st.markdown(f"**{i}. {q.get('question')}**\n\n*Rép: {q.get('reponse_attendue')}*")

        with st.expander(t("pedag_notes_title"), expanded=False):
            st.markdown(f"**{t('target_grammar')}** {res.get('point_grammatical', '')}")
            st.markdown(res.get("notes_pedagogiques", ""))

        st.markdown("---")
        export_row1 = st.columns(2)
        export_row2 = st.columns(2)
        b_col1, b_col2 = export_row1
        b_col3, b_col4 = export_row2

        with b_col1:
            if st.button(t("btn_save"), use_container_width=True):
                try:
                    save_to_archive(
                        content_type="Texte",
                        niveau=meta.get("niveau", ""),
                        projet_num=meta.get("projet_num", 0),
                        sequence_num=meta.get("sequence_num", 0),
                        theme=res.get("theme", ""),
                        title=res.get("titre", ""),
                        content_json=json.dumps(res, ensure_ascii=False),
                    )
                    st.toast(t("save_success"), icon="✅")
                except Exception as exc:
                    logger.error("Erreur sauvegarde texte: %s", exc)
                    st.error(t("save_error"))

        with b_col2:
            try:
                pdf_path = export_texte_pdf(res, "texte_export.pdf")
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label=t("btn_pdf"),
                        data=pdf_file.read(),
                        file_name="texte_support.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
            except Exception as exc:
                logger.error("Erreur export PDF texte: %s", exc)
                st.error(t("pdf_error"))

        with b_col3:
            st.download_button(
                label=t("btn_txt"),
                data=res.get("texte", ""),
                file_name="texte_support.txt",
                mime="text/plain",
                use_container_width=True,
            )

        with b_col4:
            inject_print_button()

    else:
        st.info(t("no_params_info"))
