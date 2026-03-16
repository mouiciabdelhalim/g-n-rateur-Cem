from backend.ai.gemini_client import get_gemini_client
from backend.ai.prompts import build_texte_prompt
from backend.database.db_manager import get_curriculum_entry
from backend.ai.schemas import TexteSupportSchema

def generate_texte(niveau: str, projet_num: int, sequence_num: int, theme: str = "") -> dict:
    """
    Génère un texte de support adapté au curriculum.
    Récupère le curriculum, construit le prompt, appelle Gemini, et retourne le JSON.
    """
    curr = get_curriculum_entry(niveau, projet_num, sequence_num)
    if not curr:
        raise ValueError(f"Séquence introuvable pour {niveau} P{projet_num} S{sequence_num}")
        
    prompt = build_texte_prompt(
        niveau=niveau,
        projet_title=curr["projet_title"],
        sequence_title=curr["sequence_title"],
        theme=theme,
        objectifs=curr["objectifs"],
        cefr=curr["cefr_level"]
    )
    
    try:
        gemini_client = get_gemini_client()
        result = gemini_client.generate(prompt, response_schema=TexteSupportSchema)
        
        result["_meta"] = {
            "niveau": niveau,
            "projet_num": projet_num,
            "sequence_num": sequence_num,
            "theme_demande": theme,
            "cefr_level": curr["cefr_level"]
        }
        
        return result
    except Exception as exc:
        raise Exception(f"Échec de la génération du texte : {str(exc)}") from exc
