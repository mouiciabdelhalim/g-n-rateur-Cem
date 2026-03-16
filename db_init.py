import sqlite3
import json
from backend.config import DB_PATH
from backend.database.curriculum_data import CURRICULUM

def create_tables(conn: sqlite3.Connection) -> None:
    """Créer les tables de la base de données si elles n'existent pas."""
    cursor = conn.cursor()
    
    # Table d'archive
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archive (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content_type TEXT NOT NULL,
            niveau TEXT NOT NULL,
            projet_num INTEGER NOT NULL,
            sequence_num INTEGER NOT NULL,
            theme TEXT,
            title TEXT NOT NULL,
            content_json TEXT NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_favorite BOOLEAN DEFAULT 0,
            notes TEXT
        )
    ''')
    
    # Table du curriculum
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS curriculum (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            niveau TEXT NOT NULL,
            cefr_level TEXT NOT NULL,
            projet_num INTEGER NOT NULL,
            projet_title TEXT NOT NULL,
            sequence_num INTEGER NOT NULL,
            sequence_title TEXT NOT NULL,
            competence TEXT NOT NULL,
            objectifs TEXT NOT NULL,
            themes TEXT NOT NULL,
            UNIQUE(niveau, projet_num, sequence_num)
        )
    ''')
    
    # Table de cache
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cache (
            cache_key TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des utilisateurs (authentification)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'teacher',
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des sessions de chat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            date_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Table des messages de chat
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(id) ON DELETE CASCADE
        )
    ''')
    
    conn.commit()

def populate_curriculum(conn: sqlite3.Connection) -> None:
    """Insérer les données du programme scolaire de base."""
    cursor = conn.cursor()
    
    # Vérifier si le curriculum est déjà rempli
    cursor.execute("SELECT COUNT(*) FROM curriculum")
    if cursor.fetchone()[0] > 0:
        return
        
    for item in CURRICULUM:
        cursor.execute('''
            INSERT INTO curriculum (
                niveau, cefr_level, projet_num, projet_title, 
                sequence_num, sequence_title, competence, objectifs, themes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            item["niveau"],
            item["cefr_level"],
            item["projet_num"],
            item["projet_title"],
            item["sequence_num"],
            item["sequence_title"],
            item["competence"],
            json.dumps(item["objectifs"], ensure_ascii=False),
            json.dumps(item["themes"], ensure_ascii=False)
        ))
    
    conn.commit()

def init_database() -> None:
    """Point d'entrée principal pour initialiser la BDD au démarrage de l'app."""
    with sqlite3.connect(DB_PATH) as conn:
        create_tables(conn)
        populate_curriculum(conn)
