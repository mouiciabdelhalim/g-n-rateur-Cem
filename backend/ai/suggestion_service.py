"""
suggestion_service.py — AI-powered theme suggestions for the CEM Generator.

Calls Gemini to propose 3 culturally-relevant themes for a given
curriculum entry (niveau + projet + séquence).

Usage:
    from backend.ai.suggestion_service import suggest_themes
    themes = suggest_themes("1AM", "Projet 1 title", "Séq 1 title", "A1")
    # → ["La vie en famille à Alger", "Le marché traditionnel", "Mon école"]
"""

import logging
from backend.ai.gemini_client import get_gemini_client
from backend.ai.prompts import build_suggestion_prompt
from backend.ai.schemas import SuggestionThemesSchema

logger = logging.getLogger(__name__)

_FALLBACK_THEMES = [
    "La vie en famille algérienne",
    "Le marché traditionnel",
    "Mon école, ma fierté",
]


def suggest_themes(
    niveau: str,
    projet_title: str,
    sequence_title: str,
    cefr: str,
    use_cache: bool = True,
) -> list[str]:
    """
    Return a list of 3 theme suggestions from Gemini.

    Falls back to a static default list if the API call fails or
    returns an unexpected format, so the UI never breaks.

    Args:
        niveau:         Class level, e.g. "1AM".
        projet_title:   Title of the selected project.
        sequence_title: Title of the selected sequence.
        cefr:           CEFR level, e.g. "A1".
        use_cache:      Whether to use the DB cache (default True).

    Returns:
        List of exactly 3 theme strings.
    """
    prompt = build_suggestion_prompt(niveau, projet_title, sequence_title, cefr)

    try:
        client = get_gemini_client()
        result = client.generate(prompt, use_cache=use_cache, response_schema=SuggestionThemesSchema)

        themes = result.get("themes", [])
        if isinstance(themes, list) and len(themes) >= 3:
            return [str(t).strip() for t in themes[:3]]

        logger.warning("suggest_themes: unexpected payload shape: %s", result)
        return _FALLBACK_THEMES

    except Exception as exc:
        logger.error("suggest_themes failed: %s", exc)
        return _FALLBACK_THEMES
