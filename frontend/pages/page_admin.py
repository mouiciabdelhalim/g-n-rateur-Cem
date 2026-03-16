import streamlit as st
import json
import pandas as pd
from backend.database.db_manager import (
    get_all_curriculum_entries,
    add_curriculum_entry,
    update_curriculum_entry,
    delete_curriculum_entry
)
from backend.services.auth_service import get_current_user
from frontend.translations import t

def render_page_admin():
    # SECURITY: Verify admin role
    user = get_current_user()
    if not user or user.get("role") != "admin":
        st.error(t("admin_access_denied"))
        st.stop()
        
    st.title(t("admin_title"))
    st.markdown(t("admin_subtitle"))
    
    # ── TABS ──────────────────────────────────────────────────────────────────
    tab_list, tab_add = st.tabs([t("admin_tab_list"), t("admin_tab_add")])
    
    # --- TAB 1: LISTE ET MODIFICATION ---
    with tab_list:
        st.subheader(t("admin_list_header"))
        entries = get_all_curriculum_entries()
        
        if not entries:
            st.info("Aucune donnée dans le curriculum.")
        else:
            # Prepare data for dataframe UI
            df_display = []
            for e in entries:
                df_display.append({
                    "ID": e["id"],
                    "Niveau": e["niveau"],
                    "CEFR": e["cefr_level"],
                    "Proj": e["projet_num"],
                    "Titre Projet": e["projet_title"],
                    "Seq": e["sequence_num"],
                    "Titre Seq": e["sequence_title"],
                    "Compétence": e["competence"]
                })
            
            df = pd.DataFrame(df_display)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            st.markdown("---")
            st.subheader(t("admin_edit_title"))
            
            selected_id = st.selectbox(
                t("admin_select_entry"), 
                options=[e["id"] for e in entries],
                format_func=lambda x: f"ID {x} - {next((e['niveau'] for e in entries if e['id'] == x), '')} - P{next((e['projet_num'] for e in entries if e['id'] == x), '')} S{next((e['sequence_num'] for e in entries if e['id'] == x), '')}"
            )
            
            if selected_id:
                entry = next((e for e in entries if e["id"] == selected_id), None)
                if entry:
                    with st.expander(f"Modifier l'entrée ID {selected_id}", expanded=True):
                        with st.form(f"form_edit_{selected_id}"):
                            col1, col2 = st.columns(2)
                            with col1:
                                edit_niv = st.selectbox("Niveau", ["1AM", "2AM", "3AM", "4AM"], index=["1AM", "2AM", "3AM", "4AM"].index(entry["niveau"]))
                                edit_cefr = st.text_input("Niveau CEFR", value=entry["cefr_level"])
                                edit_pnum = st.number_input("N° Projet", min_value=1, value=entry["projet_num"], step=1)
                                edit_ptitle = st.text_input("Titre du Projet", value=entry["projet_title"])
                            with col2:
                                edit_snum = st.number_input("N° Séquence", min_value=1, value=entry["sequence_num"], step=1)
                                edit_stitle = st.text_input("Titre de la Séquence", value=entry["sequence_title"])
                                edit_comp = st.text_area("Compétence visée", value=entry["competence"], height=100)
                                
                            edit_obj = st.text_area("Objectifs (séparés par un retour à la ligne)", value="\\n".join(json.loads(entry["objectifs"])))
                            edit_themes = st.text_area("Thèmes (séparés par un retour à la ligne)", value="\\n".join(json.loads(entry["themes"])))
                                
                            col_submit, col_delete = st.columns([1, 1])
                            with col_submit:
                                if st.form_submit_button(t("btn_save"), type="primary", use_container_width=True):
                                    updated_data = {
                                        "niveau": edit_niv,
                                        "cefr_level": edit_cefr,
                                        "projet_num": edit_pnum,
                                        "projet_title": edit_ptitle,
                                        "sequence_num": edit_snum,
                                        "sequence_title": edit_stitle,
                                        "competence": edit_comp,
                                        "objectifs": [o.strip() for o in edit_obj.split("\\n") if o.strip()],
                                        "themes": [t.strip() for t in edit_themes.split("\\n") if t.strip()]
                                    }
                                    try:
                                        update_curriculum_entry(selected_id, updated_data)
                                        st.success(t("admin_update_success"))
                                        st.rerun()
                                    except Exception as err:
                                        st.error(f"Erreur de mise à jour: {err}")
                            with col_delete:
                                pass # Form limits delete buttons so we handle it below

                        if st.button("🗑️ " + t("admin_delete_btn"), key=f"del_{selected_id}", type="secondary", use_container_width=True):
                            try:
                                delete_curriculum_entry(selected_id)
                                st.success(t("admin_delete_success"))
                                st.rerun()
                            except Exception as err:
                                st.error(f"Erreur de suppression: {err}")


    # --- TAB 2: AJOUTER UNE NOUVELLE ENTREE ---
    with tab_add:
        st.subheader(t("admin_add_header"))
        with st.form("form_add_curriculum"):
            col1, col2 = st.columns(2)
            with col1:
                add_niv = st.selectbox("Niveau", ["1AM", "2AM", "3AM", "4AM"])
                add_cefr = st.text_input("Niveau CEFR", value="A1")
                add_pnum = st.number_input("N° Projet", min_value=1, value=1, step=1)
                add_ptitle = st.text_input("Titre du Projet", placeholder="Ex: Projet 1")
            with col2:
                add_snum = st.number_input("N° Séquence", min_value=1, value=1, step=1)
                add_stitle = st.text_input("Titre de la Séquence", placeholder="Ex: Séquence 1")
                add_comp = st.text_area("Compétence visée", placeholder="La compétence terminale...", height=100)
                
            add_obj = st.text_area("Objectifs (séparés par un retour à la ligne)", placeholder="Objectif 1\\nObjectif 2")
            add_themes = st.text_area("Thèmes (séparés par un retour à la ligne)", placeholder="Le voyage\\nLa nature")
                
            if st.form_submit_button(t("admin_add_btn"), type="primary", use_container_width=True):
                new_data = {
                    "niveau": add_niv,
                    "cefr_level": add_cefr,
                    "projet_num": add_pnum,
                    "projet_title": add_ptitle,
                    "sequence_num": add_snum,
                    "sequence_title": add_stitle,
                    "competence": add_comp,
                    "objectifs": [o.strip() for o in add_obj.split("\\n") if o.strip()],
                    "themes": [t.strip() for t in add_themes.split("\\n") if t.strip()]
                }
                try:
                    add_curriculum_entry(new_data)
                    st.success(t("admin_add_success"))
                    st.rerun()
                except Exception as err:
                    st.error(f"Erreur d'ajout: {err}")
