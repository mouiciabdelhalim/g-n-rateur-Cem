import streamlit as st
from backend.database.db_manager import get_db_stats, get_archive
from frontend.translations import t

def render_page_accueil():
    st.title(t("dashboard_title"))
    st.markdown(t("welcome_msg"))
    st.markdown("---")

    # ── Statistiques ──────────────────────────────────────────────────────────
    stats = get_db_stats()
    total = stats.get('textes_count', 0) + stats.get('grilles_count', 0) + stats.get('situations_count', 0)

    st.subheader(t("stats_title"))
    row1 = st.columns(2)
    row2 = st.columns(2)
    with row1[0]:
        st.metric(t("stat_textes"), stats.get('textes_count', 0))
    with row1[1]:
        st.metric(t("stat_grilles"), stats.get('grilles_count', 0))
    with row2[0]:
        st.metric(t("stat_situations"), stats.get('situations_count', 0))
    with row2[1]:
        st.metric(t("stat_total"), total)

    st.markdown("---")

    # ── Démarrage rapide ──────────────────────────────────────────────────────
    st.subheader(t("quick_start_title"))
    if st.button(t("btn_create_texte"), use_container_width=True, type="primary"):
        st.session_state["current_page"] = "texte"
        st.rerun()
    if st.button(t("btn_create_grille"), use_container_width=True, type="primary"):
        st.session_state["current_page"] = "grille"
        st.rerun()
    if st.button(t("btn_create_situation"), use_container_width=True, type="primary"):
        st.session_state["current_page"] = "situation"
        st.rerun()

    st.markdown("---")

    # ── Derniers documents ────────────────────────────────────────────────────
    st.subheader(t("recent_archives_title"))
    recent = get_archive()[:5]

    if not recent:
        st.info(t("no_archives_msg"))
    else:
        for doc in recent:
            icon = {"Texte": "📝", "Grille": "📊", "Situation": "🎯"}.get(doc.get("content_type", ""), "📄")
            col_a, col_b, col_c = st.columns([3, 1, 1])
            with col_a:
                titulo = doc.get("title", "")
                titulo = titulo if titulo else t("untitled")
                st.markdown(f"**{icon} {titulo}**")
            with col_b:
                st.caption(doc.get("niveau", ""))
            with col_c:
                date_str = doc.get("date_created", "")[:10] if doc.get("date_created") else ""
                st.caption(date_str)
        
        if st.button(t("btn_view_all_archives"), use_container_width=False):
            st.session_state["current_page"] = "archive"
            st.rerun()
