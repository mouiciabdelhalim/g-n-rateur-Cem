import logging
from backend.ai.schemas import AnalyseTexteSchema
from backend.ai.prompts import build_analyse_prompt
from backend.ai.gemini_client import get_gemini_client

logger = logging.getLogger(__name__)

def analyze_texte(
    texte_source: str,
    niveau: str,
    projet_num: int,
    sequence_num: int,
    use_cache: bool = True
) -> dict:
    """
    Analyse un texte fourni par l'utilisateur pour extraire le vocabulaire, 
    les questions, la grammaire et valider le niveau CECR.
    """
    from backend.services.texte_service import CEFR_MAP, CEFR_CURRICULUM
    
    cefr = CEFR_MAP.get(niveau, "A1")
    
    # Récupérer les titres de projet et séquence depuis le scope (optionnel, mais donne plus de contexte)
    projet_title = ""
    sequence_title = ""
    try:
        if niveau in CEFR_CURRICULUM:
            for p in CEFR_CURRICULUM[niveau]:
                if p["projet"] == projet_num:
                    projet_title = p["titre"]
                    for s in p["sequences"]:
                        if s["sequence"] == sequence_num:
                            sequence_title = s["titre"]
                            break
                    break
    except Exception as e:
        logger.warning(f"Erreur lors de la récupération du curriculum pour l'analyse: {e}")

    prompt = build_analyse_prompt(
        texte_source=texte_source,
        niveau=niveau,
        projet_title=projet_title,
        sequence_title=sequence_title,
        cefr=cefr
    )
    
    gemini_client = get_gemini_client()
    result = gemini_client.generate(
        prompt=prompt,
        use_cache=use_cache,
        response_schema=AnalyseTexteSchema
    )
    
    # Injecter les métadonnées pour l'archivage ou l'affichage
    result["_meta"] = {
        "niveau": niveau,
        "cefr_level": cefr,
        "projet_num": projet_num,
        "sequence_num": sequence_num,
        "texte_source": texte_source
    }
    
    return result
