import streamlit as st
from datetime import datetime
from frontend.translations import t

MAX_DRAFTS = 5

def add_draft(page_key: str, result: dict) -> None:
    """Ajoute le résultat généré aux brouillons de la session."""
    drafts_key = f"drafts_{page_key}"
    if drafts_key not in st.session_state:
        st.session_state[drafts_key] = []
        
    # Ajouter un horodatage
    draft_entry = {
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "data": result
    }
    
    # Insérer au début de la liste
    st.session_state[drafts_key].insert(0, draft_entry)
    
    # Limiter à MAX_DRAFTS
    if len(st.session_state[drafts_key]) > MAX_DRAFTS:
        st.session_state[drafts_key] = st.session_state[drafts_key][:MAX_DRAFTS]

def render_drafts_ui(page_key: str, target_state_key: str) -> None:
    """Affiche l'interface des brouillons et permet la restauration."""
    drafts_key = f"drafts_{page_key}"
    drafts = st.session_state.get(drafts_key, [])
    
    if not drafts:
        return
        
    st.markdown("---")
    with st.expander(f"🕒 {t('drafts_header')} ({len(drafts)})"):
        st.warning(t('drafts_warning'))
        
        for i, draft in enumerate(drafts):
            data = draft["data"]
            # Essayer de trouver un titre lisible
            title = data.get("titre") or data.get("titre_fiche") or t("untitled_draft")
            time_str = draft["timestamp"]
            
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(f"**{time_str}** - {title}")
            with col_btn:
                if st.button(t("btn_restore"), key=f"restore_{page_key}_{i}", use_container_width=True):
                    st.session_state[target_state_key] = data
                    st.rerun()
