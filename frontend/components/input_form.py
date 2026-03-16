import streamlit as st
from backend.database.db_manager import get_projets_by_niveau, get_sequences_by_niveau_projet
from frontend.translations import t

def render_curriculum_form(form_key: str) -> dict | None:
    """
    Renders Niveau → Projet → Séquence cascading selectors.
    Returns dict with selected values when submitted, None otherwise.
    Uses st.session_state to persist selections.
    """
    st.write(f"### {t('curriculum_title')}")
    
    niveau_key = f"{form_key}_niveau"
    projet_key = f"{form_key}_projet"
    sequence_key = f"{form_key}_sequence"
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        niveaux = ["1AM", "2AM", "3AM", "4AM"]
        selected_niveau = st.selectbox(
            "Niveau", 
            niveaux, 
            format_func=lambda x: t(f"niveau_{x.lower()}"),
            key=niveau_key
        )
        
    with col2:
        projets = get_projets_by_niveau(selected_niveau)
        projet_options = {p['projet_title']: p['projet_num'] for p in projets}
        selected_projet_title = None
        
        if projet_options:
            selected_projet_title = st.selectbox(
                t("projet_label"), 
                list(projet_options.keys()),
                key=projet_key
            )
            selected_projet_num = projet_options[selected_projet_title]
        else:
            st.warning(t("no_projet"))
            selected_projet_num = None
            
    with col3:
        selected_sequence_title = None
        if selected_projet_num:
            sequences = get_sequences_by_niveau_projet(selected_niveau, selected_projet_num)
            sequence_options = {s['sequence_title']: s['sequence_num'] for s in sequences}
            
            if sequence_options:
                selected_sequence_title = st.selectbox(
                    t("sequence_label"), 
                    list(sequence_options.keys()),
                    key=sequence_key
                )
                selected_sequence_num = sequence_options[selected_sequence_title]
            else:
                st.warning(t("no_sequence"))
                selected_sequence_num = None
        else:
            selected_sequence_num = None

    if selected_niveau and selected_projet_num and selected_sequence_num:
        return {
            "niveau": selected_niveau,
            "projet_num": selected_projet_num,
            "sequence_num": selected_sequence_num,
            "projet_title": selected_projet_title,
            "sequence_title": selected_sequence_title
        }
    return None

