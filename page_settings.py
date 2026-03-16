import streamlit as st
import os
import re
import logging
from dotenv import set_key
from backend.database.db_manager import clear_cache, get_db_stats
from backend.utils.backup import backup_database
from frontend.translations import t

logger = logging.getLogger(__name__)

# SECURITY: compute the .env path once, absolutely, at import time
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_ENV_PATH = os.path.join(_PROJECT_ROOT, ".env")

# SECURITY: validate that a key looks like a real Google API key (39 chars, starts with AIza)
_API_KEY_RE = re.compile(r'^AIza[0-9A-Za-z\-_]{35}$')

def render_page_settings():
    st.title(t("settings_title"))
    
    st.header(t("lang_section_title"))
    lang_opts = {"fr": "Français", "ar": "العربية"}
    current_lang = st.session_state.get("lang", "fr")
    
    # Toggle language
    new_lang = st.radio(t("lang_toggle_label"), options=list(lang_opts.keys()), format_func=lambda x: lang_opts[x], index=0 if current_lang == "fr" else 1, horizontal=True)
    if new_lang != current_lang:
        st.session_state["lang"] = new_lang
        st.rerun()

    st.markdown("---")
    
    st.header(t("api_section_title"))
    
    current_key = os.getenv("GEMINI_API_KEY", "")
    new_key = st.text_input(t("api_key_label"), value=current_key, type="password")
    
    # Available models list
    model_options = ["gemini-3.1-pro-preview", "gemini-3.0-flash", "gemini-2.5-pro", "gemini-2.5-flash"]
    current_model = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")
    current_model_index = model_options.index(current_model) if current_model in model_options else 0
    
    current_temp = float(os.getenv("GENERATION_TEMPERATURE", "0.4"))
    
    col1, col2 = st.columns(2)
    with col1:
        model = st.selectbox(t("model_label"), model_options, index=current_model_index)
    with col2:
        temp = st.slider(t("temp_label"), min_value=0.0, max_value=1.0, value=current_temp, step=0.1)
        
    if st.button(t("btn_save_api"), type="primary"):
        try:
            has_changes = False
            
            # Save API key if changed
            if new_key and new_key != current_key:
                # SECURITY FIX: validate key format before writing to disk
                if not _API_KEY_RE.match(new_key):
                    st.error(t("api_format_err"))
                    st.stop()
                if not os.path.exists(_ENV_PATH):
                    with open(_ENV_PATH, "w", encoding="utf-8") as f:
                        f.write(f"GEMINI_API_KEY={new_key}\n")
                else:
                    set_key(_ENV_PATH, "GEMINI_API_KEY", new_key)
                os.environ["GEMINI_API_KEY"] = new_key
                has_changes = True
            
            # Save model if changed
            if model != current_model:
                set_key(_ENV_PATH, "GEMINI_MODEL", model)
                os.environ["GEMINI_MODEL"] = model
                has_changes = True
            
            # Save temperature if changed
            if abs(temp - current_temp) > 0.01:
                set_key(_ENV_PATH, "GENERATION_TEMPERATURE", str(temp))
                os.environ["GENERATION_TEMPERATURE"] = str(temp)
                has_changes = True
            
            if has_changes:
                st.cache_resource.clear()
                st.success(t("api_save_success"))
            else:
                st.info(t("api_no_change"))
        except Exception as exc:
            # SECURITY FIX: log real error internally, show generic message to user
            logger.error("Erreur enregistrement .env: %s", exc)
            st.error(t("api_save_err"))
            
    st.markdown("---")
    st.header(t("cache_section_title"))
    st.info(t("cache_info"))
    
    cache_enabled = st.toggle(t("cache_toggle"), value=True)
    if st.button(t("btn_clear_cache")):
        clear_cache()
        st.success(t("cache_cleared"))
        
    st.markdown("---")
    st.header(t("db_section_title"))
    
    stats = get_db_stats()
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric(t("stat_textes"), stats.get('textes_count', 0))
    col_s2.metric(t("stat_situations"), stats.get('situations_count', 0))
    col_s3.metric(t("stat_grilles"), stats.get('grilles_count', 0))
    col_s4.metric(t("db_size"), f"{stats.get('db_size_mb', 0)} MB")
    
    st.markdown("##### " + t("backup_info"))
    if st.button(t("btn_create_backup"), type="secondary"):
        with st.spinner("..."):
            dest_path = backup_database()
            if dest_path:
                st.success(t("backup_success", path=dest_path))
            else:
                st.error(t("backup_error"))

    st.markdown("---")
    st.header(t("danger_section_title"))
    
    confirm = st.checkbox(t("danger_confirm"))
    if st.button(t("btn_reset_archive"), type="primary", disabled=not confirm):
        import sqlite3
        from backend.config import DB_PATH
        try:
            with sqlite3.connect(DB_PATH) as conn:
                conn.cursor().execute("DELETE FROM archive")
                conn.commit()
            st.success(t("reset_success"))
            st.rerun()
        except Exception as e:
            st.error(str(e))
