# Générateur Pédagogique CEM

Outil pédagogique pour l'enseignement du FLE (Français Langue Étrangère) dans les collèges algériens.
Application propulsée par l'intelligence artificielle (Google Gemini).

## 🌟 Fonctionnalités Principales (Features)

**1. 💬 Interface de Chat Dynamique (Professeur NADIA)**
- **Sauvegarde Automatique** : Les conversations sont automatiquement enregistrées dans la base de données locale (`SQLite`).
- **Historique et Restauration** : Reprenez vos anciennes discussions depuis la barre latérale. L'IA se souviendra du contexte.
- **Gestion des Sessions** : Créez une **Nouvelle session** à tout moment ou **Supprimez** les anciennes conversations.
- **Streaming en temps réel** : Les réponses de l'IA s'affichent de façon dynamique, caractère par caractère (effet machine à écrire).
- **Design Premium** : UI soignée avec des bulles de chat distinctes (utilisateur vs. assistant).

**2. 📑 Fiche de Préparation (Lesson Planning)**
- Génération automatisée des fiches de préparation adaptées au curriculum algérien (Niveau, Projet, Séquence).
- Structuration selon les normes officielles du CEM.

**3. 📝 Analyse de Texte Intelligente**
- **Upload de Documents** : Importez des textes pour une analyse pédagogique par l'IA.
- **Extraction** : Identification du vocabulaire clé, des points de grammaire et d'orthographe.
- **Évaluation CECRL** : L'IA estime le niveau CECRL (A1, A2, B1, etc.) du texte importé pour garantir sa pertinence vis-à-vis des élèves.

**4. 🌐 Support Multilingue & 🌙 Thème Sombre**
- Interface disponible en Français et en Arabe (avec support RTL correct).
- Choix de mode clair ou sombre (Dark Mode) natif.

**5. ⚙️ Personnalisation des Modèles**
- Support des différents modèles Google Gemini (1.5 Flash, 2.5 Pro, 3.1 Pro etc.) avec sauvegarde persistante des paramètres.

## 🛠️ Installation

1. Cloner le dépôt et naviguer dans le dossier du projet :
```bash
cd cem_generator
```
2. Installer les dépendances :
```bash
pip install -r requirements.txt
```
3. Ajouter votre clé API dans le fichier `.env` :
```env
GEMINI_API_KEY=votre_cle_ici
```
4. Lancer l'application :
```bash
streamlit run frontend/app.py
```

## 📜 Licence

Ce projet est distribué sous la [Licence MIT](LICENSE). Voir le fichier `LICENSE` pour plus d'informations.
