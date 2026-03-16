import streamlit as st
from frontend.translations import t
from backend.services.auth_service import get_current_user, logout

def render_sidebar():
    """Renders the main navigation sidebar."""
    with st.sidebar:
        # ── User Info ──────────────────────────────────────────────
        user = get_current_user()
        if user:
            st.markdown(f"""
            <div style="text-align: center; margin-bottom: 15px; padding: 12px; 
                        background: linear-gradient(135deg, rgba(79,139,249,0.1), rgba(0,191,165,0.1)); 
                        border-radius: 12px; border: 1px solid rgba(79,139,249,0.15);">
                <div style="font-size: 2rem; margin-bottom: 4px;">👨‍🏫</div>
                <div style="color: #4F8BF9; font-weight: 600; font-size: 0.95rem;">{user['full_name']}</div>
                <div style="color: #6666aa; font-size: 0.75rem;">@{user['username']}</div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 30px;">
            <h1 style="color: #4F8BF9; margin-bottom: 0;">{t("sidebar_title")}</h1>
            <p style="color: #666; font-size: 0.9em;">{t("sidebar_subtitle")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.write(f"### {t('nav_title')}")
        
        current_page = st.session_state.get("current_page", "texte")
        
        def set_page(page_name):
            st.session_state["current_page"] = page_name
            
        nav_items = [
            (t("nav_accueil"), "accueil"),
            (t("nav_texte"), "texte"),
            (t("nav_analyse"), "analyse"),
            (t("nav_situation"), "situation"),
            (t("nav_grille"), "grille"),
            (t("nav_fiche"), "fiche"),
            (t("nav_exercices"), "exercices"),
            (t("nav_evaluation"), "evaluation"),
            (t("nav_chat"), "chat"),
            (t("nav_archive"), "archive"),
        ]

        if user and user.get("role") == "admin":
            nav_items.append((t("nav_admin"), "admin"))

        nav_items.extend([
            (t("nav_guide"), "guide"),
            (t("nav_settings"), "settings"),
        ])
        
        for label, page_key in nav_items:
            is_active = current_page == page_key
            button_type = "primary" if is_active else "secondary"
            if st.button(label, key=f"nav_{page_key}", use_container_width=True, type=button_type):
                set_page(page_key)
                st.rerun()
                
        st.markdown("---")
        
        # ── Logout Button ──────────────────────────────────────────
        if st.button(t("btn_logout"), key="btn_logout", use_container_width=True):
            logout()
            st.rerun()
        
        st.caption(t("footer_text"))
