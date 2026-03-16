import hashlib
import json
import logging
import typing
from pydantic import BaseModel
from google import genai
from google.genai import types

from backend.database.db_manager import get_cache, set_cache
from backend.config import CACHE_ENABLED
from backend.ai.prompts import SYSTEM_PERSONA

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self._client = None
        self._current_api_key = None
        
    def _get_client_and_config(self):
        """Récupère la configuration la plus récente."""
        import os
        api_key = os.getenv("GEMINI_API_KEY", "")
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.1-pro-preview")
        temperature = float(os.getenv("GENERATION_TEMPERATURE", "0.4"))
        
        if self._client is None or self._current_api_key != api_key:
            self._client = genai.Client(api_key=api_key) if api_key else None
            self._current_api_key = api_key
            
        return self._client, model_name, temperature

    def generate(self, prompt: str | list, use_cache: bool = True, response_schema: typing.Type[BaseModel] | None = None) -> dict:
        """Génère du contenu avec Gemini 3 et gère le cache.
        Intègre les directives "Professeur NADIA" strictement via system_instruction.
        Accepte un string simple ou une liste de contenus (multimodal).
        Retourne un dictionnaire (JSON parsé).
        """
        client, model_name, temperature = self._get_client_and_config()
        if not client:
             raise RuntimeError("Clé API GEMINI manquante. Veuillez la configurer dans les paramètres.")
             
        # 1. Key de cache (basée sur le prompt, le schéma et le persona pour la cohérence)
        # Gestion du hachage pour liste de contenus (images, textes)
        if isinstance(prompt, list):
            # Convert list parts to a string representation for hashing safely
            prompt_hash_parts = []
            for item in prompt:
                if isinstance(item, str):
                    prompt_hash_parts.append(item)
                elif hasattr(item, "image_bytes"):
                    # Use a portion of the bytes or length to represent the image
                    prompt_hash_parts.append(f"img_{len(item.image_bytes)}")
                elif hasattr(item, "file_uri"):
                     prompt_hash_parts.append(item.file_uri)
                else:
                    prompt_hash_parts.append(str(item))
            prompt_str_for_hash = "_".join(prompt_hash_parts)
        else:
            prompt_str_for_hash = prompt
            
        hash_info = f"{SYSTEM_PERSONA}|{prompt_str_for_hash}|{str(response_schema)}"
        hash_obj = hashlib.sha256(hash_info.encode('utf-8'))
        cache_key = hash_obj.hexdigest()
        
        # 2. Vérifier le cache
        if CACHE_ENABLED and use_cache:
            cached_result = get_cache(cache_key)
            if cached_result:
                try:
                    return json.loads(cached_result)
                except json.JSONDecodeError:
                    pass
        
        # 3. Préparer la configuration de la vue Pédagogique (System Persona & Température)
        config_kwargs = {
            "system_instruction": SYSTEM_PERSONA,
            "temperature": temperature, # Température parfaite pour créativité stricte (0.4 ou 0.5)
            "max_output_tokens": 8192,
        }
        
        if response_schema:
            config_kwargs["response_mime_type"] = "application/json"
            config_kwargs["response_schema"] = response_schema
            
        generation_config = types.GenerateContentConfig(**config_kwargs)
            
        # 4. Appel API avec gestion robuste des erreurs réseau/quotas
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=generation_config
            )
            response_text = response.text
        except Exception as exc:
            error_msg = str(exc).lower()
            
            # Analyse du type d'erreur pour remonter un message clair à l'utilisateur
            if "quota" in error_msg or "429" in error_msg:
                logger.error("Quota atteint (429) ou limite de taux : %s", exc)
                user_msg = "Quota dépassé : le service est temporairement surchargé. Veuillez réessayer dans quelques instants."
            elif "timeout" in error_msg or "deadline" in error_msg or "timed out" in error_msg:
                logger.error("Timeout API Gemini: %s", exc)
                user_msg = "Le service IA a mis trop de temps à répondre (Timeout). Veuillez réessayer."
            elif "network" in error_msg or "connection" in error_msg or "socket" in error_msg:
                logger.error("Erreur réseau vers Gemini: %s", exc)
                user_msg = "Problème de connexion avec le service IA. Vérifiez votre connexion internet."
            else:
                logger.error("Erreur inattendue lors de l'appel Gemini (SDK v3): %s", exc)
                user_msg = "Erreur inattendue avec le service IA. Veuillez réessayer plus tard."
                
            raise RuntimeError(user_msg) from None
            
        # 5. Nettoyage et Parse JSON
        if not response_text:
            raise RuntimeError("La réponse du service IA était vide de façon inattendue.")
            
        clean_text = self._clean_json_response(response_text)
        
        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError as exc:
            logger.error("Erreur de parsing JSON depuis Gemini 3.1: %s | Texte brut: %.200s", exc, clean_text)
            raise RuntimeError("La réponse de l'inspecteur IA était malformée. Veuillez réessayer.") from None
            
        # 6. Sauvegarder en cache
        if CACHE_ENABLED:
            set_cache(cache_key, json.dumps(data, ensure_ascii=False))
            
        return data

    def _clean_json_response(self, text: str) -> str:
        """Supprime les blocs markdown autour du JSON renvoyé par le LLM."""
        text = text.strip()
        if text.startswith("```json"):
            text = text[7:]
        elif text.startswith("```"):
            text = text[3:]
            
        if text.endswith("```"):
            text = text[:-3]
            
        return text.strip()
        
    def _validate_response(self, data: dict, required_keys: list) -> bool:
        """Vérifie que les clés du schéma JSON sont présentes."""
        return all(key in data for key in required_keys)

# Provide function for Streamlit DI
import streamlit as st

@st.cache_resource
def get_gemini_client() -> GeminiClient:
    """Returns a cached singleton of the GeminiClient"""
    return GeminiClient()
