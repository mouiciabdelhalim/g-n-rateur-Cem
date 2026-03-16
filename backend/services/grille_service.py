from backend.ai.gemini_client import get_gemini_client
from backend.ai.prompts import build_grille_prompt
from backend.ai.schemas import GrilleEvaluationSchema
from backend.config import CEFR_MAP

def generate_grille(niveau: str, type_production: str, competence: str, sequence_title: str = "Toute séquence", use_cache: bool = True) -> dict:
    """
    Génère une grille d'évaluation adaptée au niveau et à la compétence.
    """
    # Déduire le niveau CECR approximatif si possible
    cefr = CEFR_MAP.get(niveau, "A2")
    
    prompt = build_grille_prompt(
        niveau=niveau,
        type_production=type_production,
        competence=competence,
        sequence_title=sequence_title,
        cefr=cefr
    )
    
    try:
        gemini_client = get_gemini_client()
        result = gemini_client.generate(prompt, use_cache=use_cache, response_schema=GrilleEvaluationSchema)
        result["_meta"] = {
            "niveau": niveau,
            "type_production": type_production,
            "competence": competence,
            "sequence_title": sequence_title,
            "cefr_level": cefr
        }
        return result
    except Exception as e:
        raise Exception(f"Échec de la génération de la grille : {str(e)}")
