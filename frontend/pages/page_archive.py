import streamlit as st
import json
from backend.database.db_manager import get_archive, get_archive_item, toggle_favorite, delete_from_archive, export_full_archive
from backend.exporters.excel_exporter import export_archive_excel, export_archive_csv
from frontend.components.archive_card import render_archive_card
from frontend.translations import t

def _on_view(item_id):
    st.session_state['view_archive_id'] = item_id

def _on_fav(item_id):
    toggle_favorite(item_id)
    st.toast("Statut favori mis à jour!")

def _on_del(item_id):
    delete_from_archive(item_id)
    if st.session_state.get('view_archive_id') == item_id:
        st.session_state['view_archive_id'] = None
    st.toast("Élément supprimé!")

def render_page_archive():
    st.title(t("archive_title"))
    
    # Navigation dans l'archive si un élément est sélectionné
    if st.session_state.get('view_archive_id'):
        item_id = st.session_state['view_archive_id']
        item = get_archive_item(item_id)
        
        if item:
            if st.button(t("btn_back_archive")):
                st.session_state['view_archive_id'] = None
                st.rerun()
                
            st.markdown(f"## {item.get('title', 'Document')}")
            st.caption(f"{t('created_on')} {item.get('date_created')} • {t('type_label')} {item.get('content_type')} • {t('level_label')} {item.get('niveau')}")
            
            try:
                content = json.loads(item.get('content_json', '{}'))
                st.json(content)
            except Exception as exc:
                import logging
                logging.getLogger(__name__).error("Failed to parse archive content: %s", exc)
                st.error(t("read_error"))
        else:
            st.session_state['view_archive_id'] = None
            st.rerun()
        return

    # Vue liste normale
    filter_row1 = st.columns(2)
    filter_row2 = st.columns(2)

    with filter_row1[0]:
        search_query = st.text_input(t("search_label"), placeholder=t("search_ph"))
    with filter_row1[1]:
        niveau_filter = st.selectbox(t("level_label").replace(':', ''), [t("type_all"), "1AM", "2AM", "3AM", "4AM"])
    with filter_row2[0]:
        type_filter = st.selectbox(t("type_label").replace(':', ''), [t("type_all"), "Texte", "Situation", "Grille"])
    with filter_row2[1]:
        st.markdown("<br/>", unsafe_allow_html=True)
        fav_filter = st.checkbox(t("fav_only"), value=False)
        
    niveau = niveau_filter if niveau_filter != t("type_all") else None
    ctype = type_filter if type_filter != t("type_all") else None
    
    archives = get_archive(niveau, ctype, fav_filter, search_query)
    
    st.markdown(f"*{t('docs_found', count=len(archives))}*")
    
    if archives:
        cols = st.columns(2)
        for i, item in enumerate(archives):
            with cols[i % 2]:
                render_archive_card(item, _on_view, _on_del, _on_fav)
    else:
        st.info(t("no_docs_found"))
        
    st.markdown("---")
    st.subheader(t("global_export_title"))
    
    export_col1, export_col2 = st.columns(2)
    with export_col1:
        if st.button(t("btn_export_all_excel"), use_container_width=True):
            try:
                all_data = export_full_archive()
                path = export_archive_excel(all_data, "archive_complete.xlsx")
                with open(path, "rb") as f:
                    st.download_button(t("btn_dl_excel"), data=f.read(), file_name="archive_cem.xlsx", use_container_width=True)
            except Exception as e:
                st.error(str(e))
                
    with export_col2:
        if st.button(t("btn_export_all_csv"), use_container_width=True):
            try:
                all_data = export_full_archive()
                path = export_archive_csv(all_data, "archive_complete.csv")
                with open(path, "rb") as f:
                    st.download_button(t("btn_dl_csv"), data=f.read(), file_name="archive_cem.csv", mime="text/csv", use_container_width=True)
            except Exception as e:
                st.error(str(e))
