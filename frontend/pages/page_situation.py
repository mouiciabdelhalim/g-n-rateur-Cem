import streamlit as st
import json
import logging
from backend.services.situation_service import generate_situation
from backend.database.db_manager import save_to_archive
from backend.exporters.pdf_exporter import export_situation_pdf
from frontend.components.input_form import render_curriculum_form
from backend.utils.rate_limit import check_rate_limit, remaining_wait
from frontend.components.print_helper import inject_print_button
from frontend.translations import t

logger = logging.getLogger(__name__)

def render_page_situation():
    st.title(t("situation_title"))
    st.markdown(t("situation_subtitle"))

    # ── Input section ────────────────────────────────────────────────────
    form_data = render_curriculum_form("situation")

    gen_col, regen_col = st.columns([2, 1])
    with gen_col:
        if st.button(t("btn_gen_situation"), type="primary", use_container_width=True, disabled=not form_data):
            if not check_rate_limit("situation_gen"):
                wait = remaining_wait("situation_gen")
                st.warning(t("limit_reached", wait=wait))
            else:
                with st.spinner(t("gen_spinner")):
                    try:
                        result = generate_situation(
                            niveau=form_data["niveau"],
                            projet_num=form_data["projet_num"],
                            sequence_num=form_data["sequence_num"]
                        )
                        st.session_state["current_situation"] = result
                        st.session_state["last_situation_params"] = form_data
                        from backend.utils.draft_manager import add_draft
                        add_draft("situation", result)
                    except Exception as exc:
                        logger.error("Erreur génération situation: %s", exc)
                        st.error(t("gen_error"))
    with regen_col:
        has_prev = "last_situation_params" in st.session_state
        if st.button("🔁", use_container_width=True, disabled=not has_prev, help=t("btn_regen_help")):
            if not check_rate_limit("situation_gen"):
                st.warning(t("limit_reached", wait=remaining_wait('situation_gen')))
            else:
                p = st.session_state["last_situation_params"]
                with st.spinner(t("regen_spinner")):
                    try:
                        result = generate_situation(
                            niveau=p["niveau"], projet_num=p["projet_num"],
                            sequence_num=p["sequence_num"], use_cache=False
                        )
                        st.session_state["current_situation"] = result
                        st.rerun()
                    except Exception as exc:
                        logger.error("Erreur régénération situation: %s", exc)
                        st.error(t("regen_error"))

    # UI Brouillons
    from backend.utils.draft_manager import render_drafts_ui
    render_drafts_ui("situation", "current_situation")


    # ── Output section ────────────────────────────────────────────────────
    st.markdown("---")
    if "current_situation" in st.session_state:
        res = st.session_state["current_situation"]
        meta = res.get("_meta", {})

        st.success(f"**{res.get('titre', t('situation_title').replace('🎯 ', ''))}** ({res.get('duree_estimee', '')})")

        st.markdown(f"### {t('context_title')}")
        st.info(res.get("contexte", ""))

        st.markdown(f"### {t('support_title')}")
        st.markdown(res.get("support_fourni", ""))

        st.markdown(f"### {t('consigne_title')}")
        st.warning(res.get("consigne", ""))

        with st.expander(t("success_criteria_title"), expanded=True):
            for c in res.get("criteres_reussite", []):
                st.markdown(f"- **{c.get('critere', '')}** : {c.get('indicateurs', '')}")

        with st.expander(t("teacher_notes_title"), expanded=False):
            st.markdown(f"**{t('material_title')}** {res.get('materiel_necessaire', '')}")
            st.markdown(f"**{t('notes_title')}** {res.get('notes_enseignant', '')}")

        st.markdown("---")
        b_col1, b_col2, b_col3 = st.columns(3)

        with b_col1:
            if st.button(t("btn_save"), use_container_width=True, key="save_sit"):
                try:
                    save_to_archive(
                        content_type="Situation",
                        niveau=meta.get("niveau", ""),
                        projet_num=meta.get("projet_num", 0),
                        sequence_num=meta.get("sequence_num", 0),
                        theme="Évaluation",
                        title=res.get("titre", ""),
                        content_json=json.dumps(res, ensure_ascii=False)
                    )
                    st.toast(t("save_success_sit"), icon="✅")
                except Exception as exc:
                    logger.error("Erreur sauvegarde situation: %s", exc)
                    st.error(t("save_error_sit"))

        with b_col2:
            try:
                pdf_path = export_situation_pdf(res, "situation_export.pdf")
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(t("btn_export_pdf"), data=pdf_file.read(), file_name="situation.pdf", mime="application/pdf", use_container_width=True)
            except Exception as exc:
                logger.error("Erreur export PDF situation: %s", exc)
                st.error(t("pdf_error_sit"))

        with b_col3:
            inject_print_button()
    else:
        st.info(t("no_params_info_sit"))

