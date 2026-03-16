from backend.ai.gemini_client import get_gemini_client
from backend.ai.prompts import build_fiche_prompt
from backend.database.db_manager import get_curriculum_entry
from backend.ai.schemas import FichePreparationSchema

def generate_fiche(niveau: str, projet_num: int, sequence_num: int, domaine: str = "Compréhension de l'écrit", use_cache: bool = True) -> dict:
    """
    Génère une fiche de préparation adaptée au curriculum.
    """
    curr = get_curriculum_entry(niveau, projet_num, sequence_num)
    if not curr:
        raise ValueError(f"Séquence introuvable pour {niveau} P{projet_num} S{sequence_num}")
        
    prompt = build_fiche_prompt(
        niveau=niveau,
        projet_title=curr["projet_title"],
        sequence_title=curr["sequence_title"],
        competence=curr["competence"],
        objectifs=curr["objectifs"],
        cefr=curr["cefr_level"],
        domaine=domaine
    )
    
    try:
        gemini_client = get_gemini_client()
        result = gemini_client.generate(prompt, use_cache=use_cache, response_schema=FichePreparationSchema)
        result["_meta"] = {
            "niveau": niveau,
            "projet_num": projet_num,
            "sequence_num": sequence_num,
            "domaine": domaine,
            "cefr_level": curr["cefr_level"]
        }
        return result
    except Exception as exc:
        raise Exception(f"Échec de la génération de la fiche : {str(exc)}") from exc
