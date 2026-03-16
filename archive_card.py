import streamlit as st
import html  # ← SECURITY: escape DB-sourced strings to prevent stored XSS

def render_archive_card(item: dict, on_view, on_delete, on_toggle_fav):
    """Affiche une carte pour un élément de l'archive."""
    fav_icon = "⭐" if item.get('is_favorite') else "☆"

    # SECURITY FIX (Stored XSS): data comes from the DB and could contain
    # HTML/JS if a previous save was tampered with. Escape every field.
    safe_niveau       = html.escape(str(item.get('niveau', '')))
    safe_date         = html.escape(str(item.get('date_created', ''))[:10])
    safe_title        = html.escape(str(item.get('title', 'Sans titre')))
    safe_content_type = html.escape(str(item.get('content_type', '')))

    with st.container():
        st.markdown(f"""
        <div style="border: 1px solid #ddd; border-radius: 8px; padding: 15px; margin-bottom: 10px; background-color: white;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="background-color: #e1f5fe; color: #0288d1; padding: 3px 8px; border-radius: 12px; font-size: 0.8em;">{safe_niveau}</span>
                <span style="color: #666; font-size: 0.8em;">{safe_date}</span>
            </div>
            <h4 style="margin: 10px 0; color: #333;">{safe_title}</h4>
            <p style="color: #666; font-size: 0.9em; margin-bottom: 15px;">
                Type: {safe_content_type}
            </p>
        </div>
        """, unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.button("👁️ Voir", key=f"view_{item['id']}", on_click=on_view, args=(item['id'],), use_container_width=True)
        with col2:
            st.button(fav_icon, key=f"fav_{item['id']}", on_click=on_toggle_fav, args=(item['id'],), use_container_width=True)
        with col3:
            st.button("🗑️", key=f"del_{item['id']}", on_click=on_delete, args=(item['id'],), type="primary", use_container_width=True)
