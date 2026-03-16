import streamlit as st
import json
import logging
from backend.services.exercice_service import generate_exercices
from backend.database.db_manager import save_to_archive
from backend.exporters.pdf_exporter import export_exercices_pdf
from frontend.components.input_form import render_curriculum_form
from backend.utils.rate_limit import check_rate_limit, remaining_wait
from frontend.components.print_helper import inject_print_button
from frontend.translations import t

logger = logging.getLogger(__name__)

def render_page_exercices():
    st.title(t("exercices_title"))
    st.markdown(t("exercices_subtitle"))

    # ── Input section ────────────────────────────────────────────────────
    form_data = render_curriculum_form("exercices")
    
    st.subheader(t("types_exercices_label"))
    col1, col2 = st.columns(2)
    with col1:
        types_options = [
            t("type_ex_qcm"),
            t("type_ex_trous"),
            t("type_ex_relier"),
            t("type_ex_conjugaison")
        ]
        selected_types = st.multiselect(
            "Sélectionnez les formats souhaités",
            options=types_options,
            default=[t("type_ex_qcm"), t("type_ex_trous")]
        )
    with col2:
        theme = st.text_input(t("theme_ex_label"), placeholder=t("theme_ex_ph"))

    gen_col, regen_col = st.columns([2, 1])
    with gen_col:
        # Require form_data and at least one type
        disabled_gen = not form_data or not selected_types
        if st.button(t("btn_gen_exercices"), type="primary", use_container_width=True, disabled=disabled_gen):
            if not check_rate_limit("exercices_gen"):
                wait = remaining_wait("exercices_gen")
                st.warning(t("limit_reached", wait=wait))
            else:
                with st.spinner(t("gen_exercices_spinner")):
                    try:
                        result = generate_exercices(
                            niveau=form_data["niveau"],
                            projet_num=form_data["projet_num"],
                            sequence_num=form_data["sequence_num"],
                            types_exercices=selected_types
                        )
                        st.session_state["current_exercices"] = result
                        st.session_state["last_exercices_params"] = {
                            "form_data": form_data,
                            "types": selected_types
                        }
                        from backend.utils.draft_manager import add_draft
                        add_draft("exercices", result)
                    except Exception as exc:
                        logger.error("Erreur génération exercices: %s", exc)
                        st.error(t("gen_error"))
    with regen_col:
        has_prev = "last_exercices_params" in st.session_state
        if st.button("🔁", use_container_width=True, disabled=not has_prev, help=t("btn_regen_help")):
            if not check_rate_limit("exercices_gen"):
                st.warning(t("limit_reached", wait=remaining_wait('exercices_gen')))
            else:
                p = st.session_state["last_exercices_params"]
                with st.spinner(t("regen_spinner")):
                    try:
                        result = generate_exercices(
                            niveau=p["form_data"]["niveau"], 
                            projet_num=p["form_data"]["projet_num"],
                            sequence_num=p["form_data"]["sequence_num"],
                            types_exercices=p["types"]
                        )
                        st.session_state["current_exercices"] = result
                        st.rerun()
                    except Exception as exc:
                        logger.error("Erreur régénération exercices: %s", exc)
                        st.error(t("regen_error"))

    # UI Brouillons
    from backend.utils.draft_manager import render_drafts_ui
    render_drafts_ui("exercices", "current_exercices")

    # ── Output section ────────────────────────────────────────────────────
    st.markdown("---")
    if "current_exercices" in st.session_state:
        res = st.session_state["current_exercices"]
        meta = res.get("_meta", {})

        st.success(f"**{res.get('titre', 'Exercices')}**")
        
        theme_val = res.get('theme', '')
        if theme_val:
            st.info(f"**Thème abordé:** {theme_val}")

        exercices_list = res.get("exercices", [])
        for i, exo in enumerate(exercices_list, 1):
            with st.expander(f"Exercice {i} : {exo.get('type_exercice', 'Exercice')}", expanded=True):
                st.markdown(f"**Consigne:** {exo.get('consigne', '')}")
                st.markdown("---")
                st.markdown(exo.get('contenu', '').replace('\\n', '  \\n'))
                st.markdown("---")
                st.success(f"**Correction:** {exo.get('reponse_attendue', '')}")

        notes = res.get("notes_enseignant", "")
        if notes:
            with st.expander(t("teacher_notes_title"), expanded=False):
                st.markdown(notes)

        st.markdown("---")
        b_col1, b_col2, b_col3 = st.columns(3)

        with b_col1:
            if st.button(t("btn_save"), use_container_width=True, key="save_ex"):
                try:
                    save_to_archive(
                        content_type="Exercices",
                        niveau=meta.get("niveau", ""),
                        projet_num=meta.get("projet_num", 0),
                        sequence_num=meta.get("sequence_num", 0),
                        theme=res.get("theme", "Grammaire/Lexique"),
                        title=res.get("titre", "Exercices"),
                        content_json=json.dumps(res, ensure_ascii=False)
                    )
                    st.toast(t("save_success_ex"), icon="✅")
                except Exception as exc:
                    logger.error("Erreur sauvegarde exercices: %s", exc)
                    st.error(t("save_error"))

        with b_col2:
            try:
                pdf_path = export_exercices_pdf(res, "exercices_export.pdf")
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        t("btn_export_pdf_ex"), 
                        data=pdf_file.read(), 
                        file_name="exercices.pdf", 
                        mime="application/pdf", 
                        use_container_width=True
                    )
            except Exception as exc:
                logger.error("Erreur export PDF exercices: %s", exc)
                st.error(t("pdf_error_ex"))

        with b_col3:
            inject_print_button()
    else:
        st.info(t("no_params_info_ex"))
