"""
auth_service.py — Service d'authentification pour le CEM Generator.

Gère la connexion, l'inscription, la déconnexion et la vérification
de l'état d'authentification des utilisateurs via Streamlit session_state.
"""
import hashlib
import sqlite3
import streamlit as st
import logging
from backend.config import DB_PATH

logger = logging.getLogger(__name__)


def _hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a static salt."""
    salted = f"cem_gen_salt_{password}_2024"
    return hashlib.sha256(salted.encode('utf-8')).hexdigest()


def _get_connection():
    return sqlite3.connect(DB_PATH)


def create_user(username: str, password: str, full_name: str, role: str = "teacher") -> tuple[bool, str]:
    """
    Crée un nouvel utilisateur.
    Returns (success: bool, message: str)
    """
    username = username.strip().lower()
    full_name = full_name.strip()
    
    if not username or not password or not full_name:
        return False, "Tous les champs sont obligatoires."
    
    if len(username) < 3:
        return False, "Le nom d'utilisateur doit contenir au moins 3 caractères."
    
    if len(password) < 4:
        return False, "Le mot de passe doit contenir au moins 4 caractères."
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        # Vérifier si l'utilisateur existe déjà
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return False, "Ce nom d'utilisateur est déjà pris."
        
        password_hash = _hash_password(password)
        cursor.execute(
            "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
            (username, password_hash, full_name, role)
        )
        conn.commit()
        conn.close()
        return True, "Compte créé avec succès !"
        
    except Exception as e:
        logger.error(f"Error creating user: {e}")
        return False, "Erreur lors de la création du compte."


def authenticate(username: str, password: str) -> tuple[bool, str]:
    """
    Authentifie un utilisateur.
    Returns (success: bool, message: str).
    En cas de succès, met à jour st.session_state.
    """
    username = username.strip().lower()
    
    if not username or not password:
        return False, "Veuillez remplir tous les champs."
    
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        
        password_hash = _hash_password(password)
        cursor.execute(
            "SELECT id, username, full_name, role FROM users WHERE username = ? AND password_hash = ?",
            (username, password_hash)
        )
        user = cursor.fetchone()
        conn.close()
        
        if user:
            st.session_state["authenticated"] = True
            st.session_state["user_id"] = user[0]
            st.session_state["username"] = user[1]
            st.session_state["full_name"] = user[2]
            st.session_state["user_role"] = user[3]
            return True, f"Bienvenue, {user[2]} !"
        else:
            return False, "Nom d'utilisateur ou mot de passe incorrect."
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return False, "Erreur lors de l'authentification."


def logout():
    """Déconnecte l'utilisateur courant."""
    for key in ["authenticated", "user_id", "username", "full_name", "user_role"]:
        if key in st.session_state:
            del st.session_state[key]


def is_authenticated() -> bool:
    """Vérifie si un utilisateur est connecté."""
    return st.session_state.get("authenticated", False)


def get_current_user() -> dict | None:
    """Retourne les infos de l'utilisateur connecté ou None."""
    if not is_authenticated():
        return None
    return {
        "id": st.session_state.get("user_id"),
        "username": st.session_state.get("username"),
        "full_name": st.session_state.get("full_name"),
        "role": st.session_state.get("user_role"),
    }


def ensure_default_admin():
    """Crée le compte admin par défaut s'il n'existe pas."""
    try:
        conn = _get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            password_hash = _hash_password("admin123")
            cursor.execute(
                "INSERT INTO users (username, password_hash, full_name, role) VALUES (?, ?, ?, ?)",
                ("admin", password_hash, "Administrateur", "admin")
            )
            conn.commit()
            logger.info("Default admin account created.")
        conn.close()
    except Exception as e:
        logger.error(f"Error creating default admin: {e}")
