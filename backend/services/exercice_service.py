from backend.ai.gemini_client import get_gemini_client
from backend.ai.prompts import build_exercices_prompt
from backend.database.db_manager import get_curriculum_entry
from backend.ai.schemas import FicheExercicesSchema

def generate_exercices(niveau: str, projet_num: int, sequence_num: int, types_exercices: list) -> dict:
    """
    Génère une fiche d'exercices variée selon le curriculum et les choix de l'utilisateur.
    Récupère le curriculum, construit le prompt, appelle Gemini, et retourne le JSON.
    """
    curr = get_curriculum_entry(niveau, projet_num, sequence_num)
    if not curr:
        raise ValueError(f"Séquence introuvable pour {niveau} P{projet_num} S{sequence_num}")
        
    if not types_exercices:
        types_exercices = ["QCM", "Remplir les vides", "Relier"]
        
    prompt = build_exercices_prompt(
        niveau=niveau,
        projet_title=curr["projet_title"],
        sequence_title=curr["sequence_title"],
        objectifs=curr["objectifs"],
        cefr=curr["cefr_level"],
        types_exercices=types_exercices
    )
    
    try:
        gemini_client = get_gemini_client()
        result = gemini_client.generate(prompt, response_schema=FicheExercicesSchema)
        
        result["_meta"] = {
            "type": "exercices",
            "niveau": niveau,
            "projet_num": projet_num,
            "sequence_num": sequence_num,
            "types_exercices": types_exercices,
            "cefr_level": curr["cefr_level"]
        }
        
        return result
    except Exception as exc:
        raise Exception(f"Échec de la génération des exercices : {str(exc)}") from exc
