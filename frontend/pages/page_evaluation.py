import streamlit as st
import pandas as pd
from PIL import Image
# io and json not needed currently

from backend.services.evaluation_service import evaluate_student_copy
from frontend.translations import t
import logging

logger = logging.getLogger(__name__)

def render_page_evaluation():
    st.title(t("eval_title"))
    st.markdown(t("eval_subtitle"))
    
    # ── Input section ────────────────────────────────────────────────────
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader(t("eval_upload_title"))
        uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"])
        
    with col2:
        niveau = st.selectbox(t("niveau_label"), ["1AM", "2AM", "3AM", "4AM"])
        consigne = st.text_area(t("eval_consigne_label"), placeholder=t("eval_consigne_ph"), height=100)
        
    if uploaded_file is not None:
        try:
            image = Image.open(uploaded_file)
            with st.expander("🖼️ Aperçu de la copie", expanded=False):
                st.image(image, caption="Copie numérisée", use_container_width=True)
        except Exception as e:
            st.error(t("upload_file_error", error=str(e)))
            image = None
    else:
        image = None

    if st.button(t("btn_evaluate"), type="primary", use_container_width=True, disabled=(not image or not consigne.strip())):
        with st.spinner(t("eval_spinner")):
            try:
                result = evaluate_student_copy(
                    image_data=image,
                    consigne=consigne,
                    niveau=niveau,
                    use_cache=True
                )
                st.session_state["current_evaluation"] = result
            except Exception as exc:
                logger.error("Erreur d'évaluation copie: %s", exc)
                st.error(t("eval_error"))
                
    # ── Output section ────────────────────────────────────────────────────
    st.markdown("---")
    if "current_evaluation" in st.session_state:
        res = st.session_state["current_evaluation"]
        
        # Note Globale
        note_globale = res.get("note_globale", "?/7")
        st.success(f"### {t('eval_total_note')} : **{note_globale}**")
        st.info(f"**{t('eval_remarque')}**: {res.get('remarque_enseignant', '')}")
        
        col_text1, col_text2 = st.columns(2)
        with col_text1:
            with st.expander("📝 " + t("eval_transcription"), expanded=True):
                st.write(res.get("transcription_originale", ""))
                
        with col_text2:
            with st.expander("✨ " + t("eval_correction"), expanded=True):
                st.write(res.get("texte_corrige", ""))
                
        # Grille officielle
        st.markdown(f"### {t('eval_grille')}")
        eval_details = res.get("evaluation_detaillee", {})
        
        grille_data = []
        criteres_map = {
            "adequation_consigne": t("eval_crit_adequation"),
            "coherence_textuelle": t("eval_crit_coherence"),
            "correction_langue": t("eval_crit_langue"),
            "perfectionnement": t("eval_crit_perfect")
        }
        
        for k, label in criteres_map.items():
            c_data = eval_details.get(k, {})
            grille_data.append({
                "Critère": label,
                t("eval_crit_note"): c_data.get("note", 0),
                t("eval_crit_comment"): c_data.get("commentaire", "")
            })
            
        df_grille = pd.DataFrame(grille_data)
        st.dataframe(df_grille, use_container_width=True, hide_index=True)
        
        # Tableau des erreurs
        st.markdown(f"### {t('eval_errors_table')}")
        erreurs = res.get("erreurs_detectees", [])
        if erreurs:
            err_data = []
            for err in erreurs:
                err_data.append({
                    t("eval_err_word"): err.get("mot_ou_phrase_errone", ""),
                    t("eval_err_correction"): err.get("correction", ""),
                    t("eval_err_type"): err.get("type_erreur", "")
                })
            df_err = pd.DataFrame(err_data)
            st.dataframe(df_err, use_container_width=True, hide_index=True)
        else:
            st.success("Aucune erreur détectée !")

        # Print / Export
        from frontend.components.print_helper import inject_print_button
        inject_print_button()
