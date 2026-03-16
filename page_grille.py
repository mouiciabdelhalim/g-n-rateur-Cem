import streamlit as st
import json
import logging
import pandas as pd
from backend.services.grille_service import generate_grille
from backend.database.db_manager import save_to_archive
from backend.exporters.pdf_exporter import export_grille_pdf
from backend.exporters.excel_exporter import export_grille_excel
from backend.utils.rate_limit import check_rate_limit, remaining_wait
from frontend.components.print_helper import inject_print_button
from frontend.translations import t

logger = logging.getLogger(__name__)

def _build_dataframe(criteres: list) -> pd.DataFrame:
    """Construit un DataFrame lisible a partir de la liste de criteres."""
    df_data = []
    for c in criteres:
        nivs = c.get("niveaux", {})
        exc      = nivs.get("excellent", {})
        bien     = nivs.get("bien", {})
        passable = nivs.get("passable", {})
        ins      = nivs.get("insuffisant", {})
        df_data.append({
            "Critere": f"{c.get('nom', '')}\n({c.get('points_max', 0)} pts)",
            "Tres Satisfaisant": f"{exc.get('description', '')}\n({exc.get('points', 0)} pts)",
            "Satisfaisant":      f"{bien.get('description', '')}\n({bien.get('points', 0)} pts)",
            "Peu Satisfaisant":  f"{passable.get('description', '')}\n({passable.get('points', 0)} pts)",
            "Insuffisant":       f"{ins.get('description', '')}\n({ins.get('points', 0)} pts)",
        })
    return pd.DataFrame(df_data)

def render_page_grille():
    st.title(t("grille_title"))
    st.markdown(t("grille_subtitle"))

    # -- Input section --
    st.write(f"### {t('params_title')}")
    niveau         = st.selectbox(t("niveau_label"), ["1AM", "2AM", "3AM", "4AM"])
    type_prod      = st.radio(t("type_prod_label"), [t("type_ecrite"), t("type_orale")])
    type_prod_val  = "Ecrite" if type_prod == t("type_ecrite") else "Orale"
    competence     = st.text_input(t("comp_eval_label"), placeholder=t("comp_eval_ph"))
    sequence_title = st.text_input(t("seq_contexte_label"), placeholder=t("seq_contexte_ph"))

    gen_col, regen_col = st.columns([2, 1])
    with gen_col:
        if st.button(t("btn_gen_grille"), type="primary", use_container_width=True, disabled=not competence):
            if not check_rate_limit("grille_gen"):
                wait = remaining_wait("grille_gen")
                st.warning(t("limit_reached", wait=wait))
            else:
                with st.spinner(t("gen_spinner_grille")):
                    try:
                        result = generate_grille(niveau, type_prod_val, competence, sequence_title)
                        st.session_state["current_grille"] = result
                        st.session_state["last_grille_params"] = {
                            "niveau": niveau, "type_prod": type_prod_val,
                            "competence": competence, "sequence_title": sequence_title
                        }
                        from backend.utils.draft_manager import add_draft
                        add_draft("grille", result)
                    except Exception as exc:
                        logger.error("Erreur generation grille: %s", exc)
                        st.error(t("gen_error"))

    with regen_col:
        has_prev = "last_grille_params" in st.session_state
        if st.button("🔁", use_container_width=True, disabled=not has_prev, help=t("btn_regen_help")):
            if not check_rate_limit("grille_gen"):
                st.warning(t("limit_reached", wait=remaining_wait('grille_gen')))
            else:
                p = st.session_state["last_grille_params"]
                with st.spinner(t("regen_spinner")):
                    try:
                        result = generate_grille(p["niveau"], p["type_prod"], p["competence"], p["sequence_title"], use_cache=False)
                        st.session_state["current_grille"] = result
                        st.rerun()
                    except Exception as exc:
                        logger.error("Erreur regeneration grille: %s", exc)
                        st.error(t("regen_error"))
                        
    # UI Brouillons
    from backend.utils.draft_manager import render_drafts_ui
    render_drafts_ui("grille", "current_grille")

    # -- Output section --
    st.markdown("---")
    if "current_grille" in st.session_state:
        res = st.session_state["current_grille"]

        criteres = res.get("criteres", [])
        bareme_total = sum(c.get("points_max", 0) for c in criteres)

        st.success(f"**{res.get('titre', 'Grille')}** (Bareme: {bareme_total} pts)")

        df = _build_dataframe(criteres)
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.info(f"**{t('obs_conseils')}** {res.get('conseil_utilisation', '')}")

        with st.expander(t("edit_grille_title"), expanded=False):
            st.caption(t("edit_grille_caption"))

            edited_criteres = []
            for i, c in enumerate(criteres):
                st.markdown(f"##### Critere {i+1}")
                cols_name = st.columns([2, 1])
                with cols_name[0]:
                    nom = st.text_input(t("critere_nom"), value=c.get("nom", ""), key=f"nom_{i}")
                with cols_name[1]:
                    pts_max = st.number_input(t("pts_max"), value=float(c.get("points_max", 5)),
                                              min_value=0.0, max_value=20.0, step=0.5, key=f"pmax_{i}")

                niveaux_c = c.get("niveaux", {})
                cols_niv = st.columns(4)
                niveau_keys = [("excellent", "Tres Satisfaisant"), ("bien", "Satisfaisant"),
                               ("passable", "Peu Satisfaisant"), ("insuffisant", "Insuffisant")]
                new_niveaux = {}

                for j, (key, label) in enumerate(niveau_keys):
                    with cols_niv[j]:
                        niv_data = niveaux_c.get(key, {})
                        desc = st.text_area(f"{label} (desc)", value=niv_data.get("description", ""),
                                            height=80, key=f"{key}_desc_{i}")
                        pts  = st.number_input(t("pts"), value=float(niv_data.get("points", 0)),
                                               min_value=0.0, max_value=pts_max, step=0.5, key=f"{key}_pts_{i}")
                        new_niveaux[key] = {"description": desc, "points": pts}

                edited_criteres.append({**c, "nom": nom, "points_max": pts_max, "niveaux": new_niveaux})
                st.markdown("---")

            if st.button(t("btn_apply_mods"), type="primary", use_container_width=True):
                st.session_state["current_grille"]["criteres"] = edited_criteres
                new_total = sum(c.get("points_max", 0) for c in edited_criteres)
                st.session_state["current_grille"]["bareme_total"] = new_total
                st.success(t("apply_success", new_total=new_total))
                st.rerun()

        st.markdown("---")

        template_map = {
            t("pdf_model_officiel"):  "officiel",
            t("pdf_model_simplifie"): "simplifie",
            t("pdf_model_colore"):    "colore",
        }
        selected_label = st.radio(t("pdf_model_label"), list(template_map.keys()), horizontal=True)
        chosen_template = template_map[selected_label]

        export_row1 = st.columns(2)
        export_row2 = st.columns(2)
        b_col1, b_col2 = export_row1
        b_col3, b_col4 = export_row2

        with b_col1:
            if st.button(t("btn_save_grille"), use_container_width=True):
                try:
                    save_to_archive(
                        content_type="Grille",
                        niveau=res.get("niveau", niveau),
                        projet_num=0, sequence_num=0,
                        theme="Ecrite", # Default or should map back, omitting.
                        title=res.get("titre", ""),
                        content_json=json.dumps(res, ensure_ascii=False)
                    )
                    st.toast(t("save_success_sit"), icon="✅")
                except Exception as exc:
                    logger.error("Erreur sauvegarde grille: %s", exc)
                    st.error(t("save_error_sit"))

        with b_col2:
            try:
                pdf_path = export_grille_pdf(res, "grille.pdf", template=chosen_template)
                with open(pdf_path, "rb") as f:
                    st.download_button("PDF", data=f.read(), file_name="grille.pdf",
                                       mime="application/pdf", use_container_width=True)
            except Exception as exc:
                logger.error("Erreur export PDF grille: %s", exc)
                st.error(t("pdf_error_sit"))

        with b_col3:
            try:
                xl_path = export_grille_excel(res, "grille.xlsx")
                with open(xl_path, "rb") as f:
                    st.download_button(t("btn_excel"), data=f.read(), file_name="grille.xlsx",
                                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                       use_container_width=True)
            except Exception as exc:
                logger.error("Erreur export Excel grille: %s", exc)
                st.error(t("save_error_sit"))

        with b_col4:
            inject_print_button()

    else:
        st.info(t("no_params_info_grille"))
