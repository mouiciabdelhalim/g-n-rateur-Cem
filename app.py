import streamlit as st
import os, sys
import logging

# Permettre l'import depuis le dossier racine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Logging global ─────────────────────────────────────────────────────────────
class JSONFormatter(logging.Formatter):
    def format(self, record):
        import json
        log_record = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage()
        }
        if record.exc_info:
            log_record["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

_LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cem_app.log")
json_handler = logging.FileHandler(_LOG_FILE, encoding="utf-8")
json_handler.setFormatter(JSONFormatter())

logging.basicConfig(
    level=logging.WARNING,
    handlers=[
        json_handler,
        logging.StreamHandler(),
    ],
)
# ────────────────────────────────────────────────────────────────────────────────

from backend.database.db_init import init_database
from backend.services.auth_service import is_authenticated, ensure_default_admin
from frontend.sidebar import render_sidebar
from frontend.pages.page_accueil import render_page_accueil
from frontend.pages.page_texte import render_page_texte
from frontend.pages.page_situation import render_page_situation
from frontend.pages.page_grille import render_page_grille
from frontend.pages.page_archive import render_page_archive
from frontend.pages.page_settings import render_page_settings
from frontend.pages.page_guide import render_page_guide
from frontend.pages.page_chat import render as render_page_chat
from frontend.pages.page_login import render_page_login
from frontend.pages.page_fiche import render_page_fiche
from frontend.pages.page_exercices import render_page_exercices
from frontend.pages.page_analyse import render_page_analyse
from frontend.pages.page_admin import render_page_admin
from frontend.pages.page_evaluation import render_page_evaluation


from frontend.translations import t

st.set_page_config(
    page_title=t("app_title"),
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="collapsed"
)

logger = logging.getLogger(__name__)

def main():
    if "lang" not in st.session_state:
        st.session_state["lang"] = "fr"

    init_database()
    ensure_default_admin()
    
    # ── Injection du Design global ─────────────────────────────────────────
    from frontend.components.design import apply_global_styles, inject_footer, set_page_container_style
    apply_global_styles()
    set_page_container_style()
    inject_footer()
    # ────────────────────────────────────────────────────────────────────────
    
    # Masquer la navigation automatique de Streamlit
    st.markdown("""
    <style>
        [data-testid="stSidebarNav"] { display: none !important; }
    </style>
    """, unsafe_allow_html=True)
    
    # ── Vérification de l'authentification ─────────────────────────────────
    if not is_authenticated():
        render_page_login()
        return
    # ──────────────────────────────────────────────────────────────────────── 
    
    render_sidebar()
    
    page = st.session_state.get("current_page", "accueil")
    
    if page == "accueil":
        render_page_accueil()
    elif page == "texte":
        render_page_texte()
    elif page == "situation":
        render_page_situation()
    elif page == "grille":
        render_page_grille()
    elif page == "archive":
        render_page_archive()
    elif page == "guide":
        render_page_guide()
    elif page == "settings":
        render_page_settings()
    elif page == "chat":
        render_page_chat()
    elif page == "fiche":
        render_page_fiche()
    elif page == "exercices":
        render_page_exercices()
    elif page == "analyse":
        render_page_analyse()
    elif page == "evaluation":
        render_page_evaluation()
    elif page == "admin":
        render_page_admin()
    else:
        st.error("Page introuvable.")

    # Tâches planifiées (exécutées une fois par chargement de façon transparente)
    # L'exécution est rapide et silencieuse
    try:
        from backend.utils.backup import backup_database, cleanup_old_backups
        from backend.database.db_manager import cleanup_cache
        backup_database()
        cleanup_old_backups()
        # Vider les éléments de cache expirés (à créer)
        cleanup_cache()
    except Exception as e:
        logger.warning(f"Background tasks failed: {str(e)}")

if __name__ == "__main__":
    main()
