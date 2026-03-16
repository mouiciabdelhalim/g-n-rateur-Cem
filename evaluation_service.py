import logging
from typing import Dict, Any, Union
from PIL import Image

from backend.ai.gemini_client import get_gemini_client
from backend.ai.prompts import build_evaluation_prompt
from backend.ai.schemas import EvaluationProductionSchema
# types from google.genai was not needed here

logger = logging.getLogger(__name__)

def evaluate_student_copy(image_data: Union[Image.Image, bytes], consigne: str, niveau: str, use_cache: bool = True) -> Dict[str, Any]:
    """
    Analyse une image contenant la production écrite d'un élève.
    1. Transcrit le texte
    2. Corrige les fautes
    3. Évalue selon la grille CEM (7 points)
    
    Args:
        image_data: L'image PIL ou les bytes de l'image de la copie
        consigne: Le sujet donné à l'élève
        niveau: Le niveau scolaire (ex: '4AM')
        use_cache: Si True, tente de récupérer depuis le cache
    
    Returns:
        Dict: Le JSON conforme à EvaluationProductionSchema
    """
    logger.info("Début de l'évaluation de la copie pour le niveau %s", niveau)
    
    client = get_gemini_client()
    
    # 1. Construire le prompt textuel
    prompt_text = build_evaluation_prompt(consigne, niveau)
    
    # 2. Préparer l'objet multimodal pour Gemini
    # Le SDK Gemini accepte directement un objet PIL.Image dans la liste `contents`
    contents = [
        image_data, 
        prompt_text
    ]
    
    # 3. Lancer la génération avec le strict schéma
    try:
        response_data = client.generate(
            prompt=contents,
            use_cache=use_cache,
            response_schema=EvaluationProductionSchema
        )
        # Ajouter les métadonnées pour l'archive éventuelle
        response_data["_meta"] = {
            "niveau": niveau,
            "type": "évaluation_copie"
        }
        return response_data
    except Exception as e:
        logger.error("Erreur dans evaluate_student_copy : %s", e)
        raise RuntimeError(f"Échec de l'évaluation de la copie: {str(e)}")
