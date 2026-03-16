from pydantic import BaseModel, Field
from typing import List

# ----------------- TEXTE SUPPORT -----------------
class VocabulaireItem(BaseModel):
    mot: str = Field(description="Mot ou expression")
    definition: str = Field(description="Définition simple contextuelle")

class QuestionComprehension(BaseModel):
    question: str = Field(description="Exemple de question de compréhension")
    reponse_attendue: str = Field(description="Exemple de réponse attendue")

class TexteSupportSchema(BaseModel):
    titre: str = Field(description="Titre du texte")
    type_texte: str = Field(description="narratif, descriptif, explicatif, ou argumentatif")
    niveau_cefr: str = Field(description="Niveau CECR du texte (ex: A1, A2)")
    theme: str = Field(description="Thème principal abordé")
    texte: str = Field(description="Le contenu du texte de support. Inclure des sauts de ligne (\\n\\n) pour séparer les paragraphes.")
    vocabulaire_cle: List[VocabulaireItem] = Field(description="Liste des mots clés et leurs définitions")
    questions_comprehension: List[QuestionComprehension] = Field(description="Questions de compréhension et réponses attendues")
    point_grammatical: str = Field(description="Explication brève du point grammatical principal de la séquence présent dans le texte")
    notes_pedagogiques: str = Field(description="Conseils du Professeur NADIA pour l'exploitation en classe")

# ----------------- SUGGESTION THEMES -----------------
class SuggestionThemesSchema(BaseModel):
    themes: List[str] = Field(description="Tableau contenant exactement 3 thèmes courts (max 10 mots chacun)")

# ----------------- SITUATION INTEGRATION -----------------
class CritereReussite(BaseModel):
    critere: str = Field(description="Nom du critère de réussite")
    indicateurs: str = Field(description="Indicateurs de réussite pour ce critère")

class CritereGrille(BaseModel):
    critere: str = Field(description="Nom du critère (ex: Adéquation à la production)")
    tres_satisfaisant: str = Field(description="Descripteur pour le niveau très satisfaisant")
    satisfaisant: str = Field(description="Descripteur pour le niveau satisfaisant")
    peu_satisfaisant: str = Field(description="Descripteur pour le niveau peu satisfaisant")
    non_satisfaisant: str = Field(description="Descripteur pour le niveau non satisfaisant")

class SituationIntegrationSchema(BaseModel):
    titre: str = Field(description="Titre de la situation")
    niveau: str = Field(description="Niveau scolaire (ex: 1AM)")
    competence: str = Field(description="Rappel de la compétence visée")
    contexte: str = Field(description="Description du contexte de la situation problème (quelques phrases)")
    consigne: str = Field(description="La tâche précise que l'élève doit accomplir")
    support_fourni: str = Field(description="Description détaillée de ce qui est donné à l'élève (texte, image, tableau...)")
    criteres_reussite: List[CritereReussite] = Field(description="Liste des critères de réussite de la tâche")
    grille_evaluation: List[CritereGrille] = Field(description="Grille d'évaluation simplifiée")
    duree_estimee: str = Field(description="Durée prévue en minutes (ex: 60 minutes)")
    materiel_necessaire: str = Field(description="Matériel requis (feuille, dictionnaire...)")
    notes_enseignant: str = Field(description="Conseils pratiques pour la passation de l'évaluation")

# ----------------- GRILLE EVALUATION -----------------
class NiveauEvaluation(BaseModel):
    description: str = Field(description="Description de ce qui est attendu pour ce niveau")
    points: float = Field(description="Points attribués pour ce niveau")

class NiveauxCritere(BaseModel):
    excellent: NiveauEvaluation
    bien: NiveauEvaluation
    passable: NiveauEvaluation
    insuffisant: NiveauEvaluation

class CritereEvaluation(BaseModel):
    numero: int = Field(description="Numéro du critère")
    nom: str = Field(description="Nom du critère principal")
    description: str = Field(description="Description de ce qui est évalué")
    points_max: float = Field(description="Points maximum pour ce critère")
    niveaux: NiveauxCritere = Field(description="Les quatre niveaux d'évaluation pour ce critère")

class GrilleEvaluationSchema(BaseModel):
    titre: str = Field(description="Titre clair de la grille")
    niveau: str = Field(description="Niveau scolaire concerné (ex: 1AM)")
    type_production: str = Field(description="Le type de production (écrite, orale...)")
    competence: str = Field(description="La compétence évaluée")
    bareme_total: float = Field(description="Doit IMPÉRATIVEMENT être sur 20")
    criteres: List[CritereEvaluation] = Field(description="Liste complète des critères d'évaluation")
    observations: str = Field(description="Espace de notes prévu pour le correcteur")
    conseil_utilisation: str = Field(description="Conseils du Professeur NADIA pour l'application de cette grille")

# ----------------- FICHE DE PREPARATION -----------------
class EtapeLecon(BaseModel):
    nom_etape: str = Field(description="Nom de l'étape (ex: Mise en situation, Analyse, Application, Évaluation)")
    duree: str = Field(description="Durée estimée de l'étape (ex: 10 min)")
    objectif_etape: str = Field(description="Objectif spécifique de cette étape")
    activite_enseignant: str = Field(description="Ce que fait l'enseignant pendant cette étape (consignes, questions, explications)")
    activite_eleve: str = Field(description="Ce que fait l'élève pendant cette étape (réponses, exercices, productions)")
    supports: str = Field(description="Supports et matériels utilisés (tableau, manuel, fiche, images...)")
    modalite: str = Field(description="Modalité de travail: individuel, en binôme, en groupe, collectif")

class FichePreparationSchema(BaseModel):
    titre: str = Field(description="Titre de la leçon (ex: Rédiger un article de journal)")
    niveau: str = Field(description="Niveau scolaire (ex: 3AM)")
    projet: str = Field(description="Titre du projet pédagogique")
    sequence: str = Field(description="Titre de la séquence")
    domaine: str = Field(description="Domaine: Compréhension de l'écrit, Production écrite, Compréhension de l'oral, Production orale, Points de langue")
    competence_terminale: str = Field(description="Compétence terminale d'intégration visée")
    competence_transversale: str = Field(description="Compétence transversale mobilisée")
    objectifs_apprentissage: List[str] = Field(description="Liste des objectifs d'apprentissage spécifiques (3-5 objectifs)")
    prerequis: List[str] = Field(description="Prérequis nécessaires pour cette leçon")
    duree_totale: str = Field(description="Durée totale de la séance (ex: 60 min)")
    materiel_didactique: List[str] = Field(description="Liste du matériel didactique nécessaire (manuel, tableau, fiches...)")
    support_pedagogique: str = Field(description="Description du support pédagogique principal utilisé (texte, image, audio...)")
    etapes: List[EtapeLecon] = Field(description="Les étapes détaillées de la leçon (4-6 étapes minimum)")
    evaluation: str = Field(description="Modalités d'évaluation formative ou sommative prévues")
    remediation: str = Field(description="Stratégie de remédiation pour les élèves en difficulté")
    prolongement: str = Field(description="Activité de prolongement ou devoir à la maison")
    notes_professeur_nadia: str = Field(description="Conseils pratiques du Professeur NADIA pour réussir cette séance")

# ----------------- EXERCICES / ACTIVITES -----------------
class ExerciceItem(BaseModel):
    consigne: str = Field(description="La consigne de l'exercice")
    type_exercice: str = Field(description="Type d'exercice: 'qcm', 'trous', 'relier', 'autre'")
    contenu: str = Field(description="Le contenu de l'exercice (soit la phrase avec trous, les options pour QCM, ou les éléments à relier)")
    reponse_attendue: str = Field(description="La réponse ou la correction de l'exercice")

class FicheExercicesSchema(BaseModel):
    titre: str = Field(description="Titre de la fiche d'exercices (ex: Exercices de Grammaire et Vocabulaire)")
    niveau: str = Field(description="Niveau scolaire (ex: 2AM)")
    theme: str = Field(description="Thème ou point grammatical/lexical abordé")
    exercices: List[ExerciceItem] = Field(description="Liste des exercices générés")
    notes_enseignant: str = Field(description="Conseils de Professeur NADIA pour utiliser ces exercices")

# ----------------- ANALYSE DE TEXTE -----------------
class PointGrammaticalExtrait(BaseModel):
    point: str = Field(description="Nom du point grammatical identifié")
    explication: str = Field(description="Explication brève et exemple tiré du texte")

class AnalyseTexteSchema(BaseModel):
    niveau_cefr_estime: str = Field(description="Niveau CECR estimé du texte (ex: A1, A2, B1)")
    justification_niveau: str = Field(description="Explication courte justifiant le niveau CECR estimé en fonction du vocabulaire et de la syntaxe")
    vocabulaire_extrait: List[VocabulaireItem] = Field(description="Liste des mots clés extraits et leurs définitions simples adaptées au niveau")
    questions_comprehension: List[QuestionComprehension] = Field(description="3 à 5 questions de compréhension adaptées au texte")
    points_grammaticaux: List[PointGrammaticalExtrait] = Field(description="Points de grammaire majeurs présents dans le texte")
    conseils_pedagogiques: str = Field(description="Conseils du Professeur NADIA sur l'exploitation pédagogique de ce texte en classe")

# ----------------- EVALUATION PRODUCTION (COPIE ELEVE) -----------------
class ErreurDetectee(BaseModel):
    mot_ou_phrase_errone: str = Field(description="Le mot ou la phrase originale contenant l'erreur")
    correction: str = Field(description="La correction proposée")
    type_erreur: str = Field(description="Le type d'erreur (orthographe | grammaire | conjugaison | syntaxe)")

class NoteCommentaire(BaseModel):
    note: float = Field(description="Note attribuée pour ce critère spécifique")
    commentaire: str = Field(description="Justification brève de la note attribuée")

class EvaluationDetaillee(BaseModel):
    adequation_consigne: NoteCommentaire = Field(description="Note sur 2 pts + Commentaire")
    coherence_textuelle: NoteCommentaire = Field(description="Note sur 2 pts + Commentaire")
    correction_langue: NoteCommentaire = Field(description="Note sur 2 pts + Commentaire")
    perfectionnement: NoteCommentaire = Field(description="Note sur 1 pt + Commentaire")

class EvaluationProductionSchema(BaseModel):
    transcription_originale: str = Field(description="Le texte exact lu sur la copie, avec fautes incluses.")
    texte_corrige: str = Field(description="Le texte entièrement corrigé.")
    erreurs_detectees: List[ErreurDetectee] = Field(description="La liste des erreurs trouvées et corrigées.")
    evaluation_detaillee: EvaluationDetaillee = Field(description="L'évaluation détaillée selon la grille officielle du CEM sur 7 points.")
    note_globale: str = Field(description="La note finale sous le format 'X/7'.")
    remarque_enseignant: str = Field(description="Un commentaire global constructif et encourageant en une phrase pour l'élève.")

