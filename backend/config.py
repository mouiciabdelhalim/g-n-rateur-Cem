import os
from dotenv import load_dotenv

load_dotenv()

# API Configuration
import streamlit as st

def _get_api_key():
    # 1. Try Streamlit Secrets (Cloud)
    try:
        if "GEMINI_API_KEY" in st.secrets:
            return st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
    # 2. Try Local Environment Variable (.env)
    return os.getenv("GEMINI_API_KEY", "")

GEMINI_API_KEY: str = _get_api_key()
GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")
GENERATION_TEMPERATURE: float = float(os.getenv("GENERATION_TEMPERATURE", "0.4"))

# Database
DB_PATH: str = "cem_generator.db"

# App
APP_VERSION: str = "1.0.0"
APP_NAME: str = "Générateur Pédagogique CEM"

# Caching
CACHE_ENABLED: bool = True
CACHE_EXPIRY_HOURS: int = 24

# Export
EXPORT_DIR: str = "exports/"

# CEFR Level Mapping (centralisé pour éviter la duplication)
CEFR_MAP: dict[str, str] = {"1AM": "A1", "2AM": "A1+", "3AM": "A2", "4AM": "A2+"}
