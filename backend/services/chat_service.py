# Removed unused imports
from backend.ai.prompts import SYSTEM_PERSONA_CHAT
from google import genai
from google.genai import types
import logging

logger = logging.getLogger(__name__)

class ChatService:
    def __init__(self):
        self._client = None
        self._current_api_key = None
        
    def _get_client_and_config(self):
        import os
        api_key = os.getenv("GEMINI_API_KEY", "")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")
        temperature = float(os.getenv("GENERATION_TEMPERATURE", "0.4"))
        
        if self._client is None or self._current_api_key != api_key:
            self._client = genai.Client(api_key=api_key) if api_key else None
            self._current_api_key = api_key
            
        return self._client, model_name, temperature
            
    def get_chat_session(self, history: list = None):
        """Initialise une session de chat. history est optionnel et permet de reprendre un contexte.
        Assure que les consignes 'Professeur NADIA' sont strictement intégrées."""
        
        # Transformer l'historique Streamlit/Pydantic en objet history supporté par google-genai
        formatted_history = []
        if history:
            for msg in history:
                # Gestion selon la forme du dict
                role = msg.get("role", "user")
                # Si le texte vient des parties: msg["parts"][0]["text"], sinon msg["text"]
                text = msg.get("text", "") 
                if not text and "parts" in msg and len(msg["parts"]) > 0:
                     text = msg["parts"][0].get("text", "")
                
                formatted_history.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=text)]
                ))
        
        client, model_name, temperature = self._get_client_and_config()
        if not client:
             raise RuntimeError("Clé API GEMINI manquante. Veuillez la configurer dans les paramètres.")
             
        # Build Config with Strict Temperature (0.4) and Persona Instruction
        config = types.GenerateContentConfig(
            system_instruction=SYSTEM_PERSONA_CHAT,
            temperature=temperature, 
            max_output_tokens=8192
        )
        
        # On utilise model_name par défaut, mais avec la configuration sécurisée
        try:
            chat = client.chats.create(
                model=model_name,
                config=config,
                history=formatted_history if len(formatted_history) > 0 else None
            )
            return chat
        except Exception as exc:
            logger.error("Erreur lors de l'initialisation du Chat Gemini: %s", exc)
            raise RuntimeError("Le système a rencontré un problème d'accès à l'IA. Vérifiez votre connexion.") from None

import streamlit as st

@st.cache_resource
def get_chat_service() -> ChatService:
    """Returns a cached singleton of ChatService"""
    return ChatService()
