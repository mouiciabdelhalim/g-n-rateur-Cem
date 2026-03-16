import re

SYSTEM_PERSONA = """
You are "Professeur NADIA", a senior French language inspector in Algeria 
with 20 years of experience in middle school education (CEM - College d Enseignement Moyen).

Your expertise includes:
- The official Algerian French language curriculum (Ministère de l'Éducation Nationale)
- CEFR levels: 1AM=A1, 2AM=A1+, 3AM=A2, 4AM=A2+
- Algerian culture, geography, traditions, history, and social reality
- Pedagogical approaches: approche par compétences, approche communicative
- Algerian educational document standards

Your rules (NEVER break these):
1. Vocabulary and syntax MUST strictly match the specified CEFR level
2. Always include natural, authentic Algerian cultural references (cities, food, names, traditions)
3. Always follow the specified curriculum objectives
4. All output MUST be in French only
5. Content must be immediately usable by teachers without any modification
"""

SYSTEM_PERSONA_CHAT = """
You are "Professeur NADIA", a senior French language inspector in Algeria 
with 20 years of experience in middle school education (CEM - College d Enseignement Moyen).

You are speaking in a free chat with a teacher (your colleague/subordinate). 
Keep your tone professional, encouraging, and deeply rooted in the Algerian educational context. 
Your language is exclusively French. 
Provide pedagogical advice, lesson ideas, and clarifications on the curriculum when asked.
"""

def _get_word_count(cefr: str) -> str:
    """Retourne la plage de mots attendue en fonction du niveau CECR."""
    if cefr == "A1": return "80-120 mots"
    elif cefr == "A1+": return "120-180 mots"
    elif cefr == "A2": return "180-260 mots"
    elif cefr == "A2+": return "250-350 mots"
    return "150-250 mots"


# ── SECURITY: Prompt Injection Hardening ─────────────────────────────────────
_MAX_USER_INPUT_LEN = 200  # hard cap on user-supplied strings
_INJECTION_PATTERN = re.compile(
    r'(ignore|forget|disregard|override|system|instruction|prompt|jailbreak|\\n---)',
    re.IGNORECASE
)

def _sanitize_user_input(value: str, field_name: str = "input") -> str:
    """
    Sanitize a user-supplied string before embedding it in an LLM prompt.

    Defenses applied:
    1. Length cap - prevents resource exhaustion and large injection payloads.
    2. Control-character strip - removes null bytes and ANSI escape sequences.
    3. Injection keyword filter - flags (and redacts) obvious injection attempts.
    """
    if not isinstance(value, str):
        return ""
    # 1. Truncate
    value = value[:_MAX_USER_INPUT_LEN]
    # 2. Strip control characters (including \x00, \x1b, etc.)
    value = re.sub(r'[\x00-\x1f\x7f]', ' ', value).strip()
    # 3. Detect and neutralise obvious injection patterns
    if _INJECTION_PATTERN.search(value):
        # Replace the suspicious value with a safe placeholder
        import logging
        logging.getLogger(__name__).warning(
            "Prompt injection attempt detected in '%s': %r", field_name, value
        )
        return "[contenu non autorisé]"
    return value
# ─────────────────────────────────────────────────────────────────────────────

def build_analyse_prompt(texte_source: str, niveau: str, projet_title: str, sequence_title: str, cefr: str) -> str:
    """Construit le prompt pour l'analyse d'un texte existant."""
    # SECURITY FIX: sanitize user text
    safe_texte = _sanitize_user_input(texte_source, "texte_source")
    
    prompt = f"""
Analyse le texte de support suivant pour une classe de {niveau} (niveau CECR cible: {cefr}).

Contexte pédagogique :
- Projet : {projet_title}
- Séquence : {sequence_title}

Texte à analyser :
\"\"\"
{safe_texte}
\"\"\"

Extraire le vocabulaire clé, proposer des questions de compréhension, identifier les points grammaticaux importants
et fournir des conseils pédagogiques pour l'exploitation de ce texte en classe.
Évalue aussi le niveau CECR réel du texte et justifie ta réponse.
Tu dois impérativement respecter le schéma et la structure JSON demandée.
"""
    return prompt

def build_texte_prompt(niveau: str, projet_title: str, sequence_title: str, theme: str, objectifs: list, cefr: str) -> str:
    """Construit le prompt pour la génération d'un texte de support."""
    word_count = _get_word_count(cefr)
    obj_str = ", ".join(objectifs)
    # SECURITY FIX (Prompt Injection): sanitize the only user-controlled value
    safe_theme = _sanitize_user_input(theme, "theme") if theme else "Libre, centré sur la culture algérienne"

    prompt = f"""
Générer un texte de support pour une classe de {niveau} (niveau CECR {cefr}).

Contexte pédagogique :
- Projet : {projet_title}
- Séquence : {sequence_title}
- Thème d'intérêt : {safe_theme}
- Objectifs linguistiques et pragmatiques à intégrer : {obj_str}

Contraintes de production :
- Longueur stricte attendue : {word_count}
- Tu dois impérativement respecter le schéma et la structure JSON demandée.
"""
    return prompt


def build_suggestion_prompt(niveau: str, projet_title: str, sequence_title: str, cefr: str) -> str:
    """
    Construit un prompt léger pour obtenir 3 suggestions de thèmes adaptées
    au niveau et à la séquence sélectionnés.
    Retourne un JSON array de 3 chaînes.
    """
    return f"""
Tu es Professeur NADIA. Un enseignant prépare du matériel pédagogique pour une classe de {niveau} (CECR {cefr}).

Contexte : Projet "{projet_title}" - Séquence "{sequence_title}".

Propose exactement 3 thèmes de texte de support DIFFÉRENTS et CRÉATIFS, ancrés dans la réalité algérienne,
adaptés au niveau {cefr}, et directement exploitables en classe.
"""


def build_situation_prompt(niveau: str, projet_title: str, sequence_title: str, competence: str, objectifs: list, cefr: str) -> str:
    """Construit le prompt pour la génération d'une situation d'intégration."""
    obj_str = ", ".join(objectifs)
    
    prompt = f"""
Générer une situation d'intégration (situation problème) pour une évaluation en classe de {niveau} (niveau CECR {cefr}).

Contexte pédagogique :
- Projet : {projet_title}
- Séquence : {sequence_title}
- Compétence visée : {competence}
- Objectifs mobilisés : {obj_str}

Contraintes de production :
- La situation doit être ancrée dans la réalité socioculturelle algérienne de l'élève.
- Tu dois impérativement respecter le schéma et la structure JSON demandée.
"""
    return prompt

def build_grille_prompt(niveau: str, type_production: str, competence: str, sequence_title: str, cefr: str) -> str:
    """Construit le prompt pour la génération d'une grille d'évaluation."""
    prompt = f"""
Générer une grille d'évaluation sommative pour une production {type_production.lower()} en classe de {niveau} (niveau CECR {cefr}).

Contexte pédagogique :
- Séquence : {sequence_title}
- Compétence à évaluer : {competence}

Contraintes de production :
- Le barème total doit IMPÉRATIVEMENT être sur 20 points.
- Adapter les critères et la notation aux exigences de l'inspection (critères minimaux de perfectionnement, volume de production...).
- Tu dois impérativement respecter le schéma et la structure JSON demandée.
"""
    return prompt

def build_fiche_prompt(niveau: str, projet_title: str, sequence_title: str, competence: str, objectifs: list, cefr: str, domaine: str = "Compréhension de l'écrit") -> str:
    """Construit le prompt pour la génération d'une fiche de préparation."""
    obj_str = ", ".join(objectifs)
    safe_domaine = _sanitize_user_input(domaine, "domaine") if domaine else "Compréhension de l'écrit"
    
    prompt = f"""
Générer une fiche de préparation complète et détaillée pour une séance en classe de {niveau} (niveau CECR {cefr}).

Contexte pédagogique :
- Projet : {projet_title}
- Séquence : {sequence_title}
- Compétence visée : {competence}
- Domaine d'activité : {safe_domaine}
- Objectifs linguistiques et pragmatiques : {obj_str}

Contraintes de production :
- Respecter strictement le format officiel algérien de la fiche de préparation du CEM.
- Inclure absolument toutes les étapes: mise en situation, analyse/compréhension, application, évaluation.
- Chaque étape doit préciser: durée, activité enseignant, activité élève, supports, modalité de travail.
- Les activités doivent être concrètes, réalistes et immédiatement exploitables.
- Les supports doivent être ancrés dans la culture et la réalité algérienne.
- Les prérequis doivent être vérifiables et pertinents.
- La remédiation doit proposer des solutions concrètes.
- Tu dois impérativement respecter le schéma et la structure JSON demandée.
"""
    return prompt

def build_exercices_prompt(niveau: str, projet_title: str, sequence_title: str, objectifs: list, cefr: str, types_exercices: list) -> str:
    """Construit le prompt pour la génération d'une fiche d'exercices d'entraînement."""
    obj_str = ", ".join(objectifs)
    types_str = ", ".join(types_exercices)
    
    prompt = f"""
Générer une fiche d'exercices et d'activités (grammaire, conjugaison, orthographe, ou vocabulaire) pour une classe de {niveau} (niveau CECR {cefr}).

Contexte pédagogique :
- Projet : {projet_title}
- Séquence : {sequence_title}
- Objectifs linguistiques abordés : {obj_str}

Contraintes de production :
- Les thèmes abordés dans les phrases doivent être pertinents pour l'âge et la culture algérienne.
- Produis une série d'exercices pertinents pour les points linguistiques de la séquence.
- Les types d'exercices souhaités sont : {types_str}. Veille à varier les formats.
- Le contenu ('contenu') de chaque 'ExerciceItem' doit être formaté clairement pour faciliter sa présentation sur un document (ex: texte à trous avec des "___", QCM avec "a) ... b) ...", etc.).
- Chaque exercice doit avoir une 'reponse_attendue' claire.
- Tu dois impérativement respecter le schéma et la structure JSON demandée.
"""
    return prompt

def build_evaluation_prompt(consigne: str, niveau: str) -> str:
    """Construit le prompt pour l'évaluation multimodale d'une copie d'élève (OCR + Notation)."""
    # Sanitize user input
    safe_consigne = _sanitize_user_input(consigne, "consigne")
    
    prompt = f"""
Tu es un inspecteur et professeur de français expert au cycle moyen (CEM) en Algérie. 
Ta mission est d'analyser l'image ci-jointe contenant la production écrite d'un élève de {niveau}.
Tu dois transcrire le texte, corriger les erreurs et l'évaluer selon la grille officielle du Ministère de l'Éducation Nationale.

Sujet / Consigne donnée à l'élève :
"{safe_consigne}"

Voici les étapes strictes à suivre :

1. TRANSCRIPTION (OCR) :
- Lis attentivement l'écriture manuscrite sur l'image fournie.
- Transcris le texte fidèlement, mot pour mot, même s'il y a des fautes. 
- Si un mot est totalement illisible, remplace-le par "[illisible]".

2. CORRECTION ET ANALYSE DES ERREURS :
- Identifie les erreurs (orthographe, grammaire, conjugaison, syntaxe).
- Propose le texte entièrement corrigé.

3. ÉVALUATION (GRILLE CEM) :
Évalue la production sur une note totale de 7 points (barème standard pour la production écrite au CEM), répartie selon ces 4 critères :
- adequation_consigne: Adéquation à la consigne / Compréhension du sujet (0 à 2 pts)
- coherence_textuelle: Cohérence textuelle (Organisation des idées, utilisation des connecteurs) (0 à 2 pts)
- correction_langue: Correction de la langue (Syntaxe, vocabulaire, orthographe, conjugaison) (0 à 2 pts)
- perfectionnement: Perfectionnement (Originalité, présentation, propreté) (0 à 1 pt)

Tu dois impérativement respecter le schéma et la structure JSON d'évaluation demandée.
"""
    return prompt
