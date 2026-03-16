import sqlite3
import json
from datetime import datetime, timedelta
from backend.config import DB_PATH, CACHE_EXPIRY_HOURS

def get_connection() -> sqlite3.Connection:
    """Obtenir une connexion à la base de données."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_projets_by_niveau(niveau: str) -> list[dict]:
    """Obtenir la liste des projets pour un niveau donné."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT projet_num, projet_title 
            FROM curriculum 
            WHERE niveau = ? 
            ORDER BY projet_num
        ''', (niveau,))
        return [dict(row) for row in cursor.fetchall()]

def get_sequences_by_niveau_projet(niveau: str, projet_num: int) -> list[dict]:
    """Obtenir les séquences pour un niveau et un projet donnés."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT sequence_num, sequence_title 
            FROM curriculum 
            WHERE niveau = ? AND projet_num = ? 
            ORDER BY sequence_num
        ''', (niveau, projet_num))
        return [dict(row) for row in cursor.fetchall()]

def get_curriculum_entry(niveau: str, projet_num: int, sequence_num: int) -> dict:
    """Récupérer les détails d'une séquence spécifique."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM curriculum 
            WHERE niveau = ? AND projet_num = ? AND sequence_num = ?
        ''', (niveau, projet_num, sequence_num))
        row = cursor.fetchone()
        
        if row:
            result = dict(row)
            try:
                result['objectifs'] = json.loads(result['objectifs'])
                result['themes'] = json.loads(result['themes'])
            except:
                pass
            return result
        return {}

def get_all_curriculum_entries() -> list[dict]:
    """Récupère toutes les entrées du curriculum pour l'administration."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM curriculum ORDER BY niveau, projet_num, sequence_num')
        return [dict(row) for row in cursor.fetchall()]

def add_curriculum_entry(data: dict) -> int:
    """Ajoute une nouvelle entrée au curriculum."""
    # Convert lists to JSON strings for storage
    objectifs_str = json.dumps(data.get("objectifs", []), ensure_ascii=False)
    themes_str = json.dumps(data.get("themes", []), ensure_ascii=False)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO curriculum (
                niveau, cefr_level, projet_num, projet_title, 
                sequence_num, sequence_title, competence, objectifs, themes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data["niveau"], data.get("cefr_level", "A1"), data["projet_num"], data["projet_title"],
            data["sequence_num"], data["sequence_title"], data["competence"], objectifs_str, themes_str
        ))
        conn.commit()
        return cursor.lastrowid

def update_curriculum_entry(entry_id: int, data: dict) -> None:
    """Met à jour une entrée du curriculum existante."""
    objectifs_str = json.dumps(data.get("objectifs", []), ensure_ascii=False)
    themes_str = json.dumps(data.get("themes", []), ensure_ascii=False)
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE curriculum SET
                niveau = ?, cefr_level = ?, projet_num = ?, projet_title = ?, 
                sequence_num = ?, sequence_title = ?, competence = ?, objectifs = ?, themes = ?
            WHERE id = ?
        ''', (
            data["niveau"], data.get("cefr_level", "A1"), data["projet_num"], data["projet_title"],
            data["sequence_num"], data["sequence_title"], data["competence"], objectifs_str, themes_str,
            entry_id
        ))
        conn.commit()

def delete_curriculum_entry(entry_id: int) -> None:
    """Supprime une entrée du curriculum."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM curriculum WHERE id = ?", (entry_id,))
        conn.commit()


def save_to_archive(content_type: str, niveau: str, projet_num: int, sequence_num: int, 
                   theme: str, title: str, content_json: str) -> int:
    """Sauvegarder un contenu généré dans les archives."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO archive (
                content_type, niveau, projet_num, sequence_num, 
                theme, title, content_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (content_type, niveau, projet_num, sequence_num, theme, title, content_json))
        conn.commit()
        return cursor.lastrowid

def get_archive(niveau: str = None, content_type: str = None, 
                favorites_only: bool = False, search_query: str = None) -> list[dict]:
    """Récupérer une liste filtrée des documents archivés."""
    query = "SELECT id, content_type, niveau, title, date_created, is_favorite FROM archive WHERE 1=1"
    params = []
    
    if niveau:
        query += " AND niveau = ?"
        params.append(niveau)
    if content_type:
        query += " AND content_type = ?"
        params.append(content_type)
    if favorites_only:
        query += " AND is_favorite = 1"
    if search_query:
        query += " AND (title LIKE ? OR theme LIKE ?)"
        params.extend([f"%{search_query}%", f"%{search_query}%"])
        
    query += " ORDER BY date_created DESC"
    
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]

def get_archive_item(archive_id: int) -> dict:
    """Récupérer le contenu complet d'un item archivé."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM archive WHERE id = ?", (archive_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return {}

def update_archive_notes(archive_id: int, notes: str) -> None:
    """Mettre à jour les notes pédagogiques pour un document archivé."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE archive SET notes = ? WHERE id = ?", (notes, archive_id))
        conn.commit()

def toggle_favorite(archive_id: int) -> None:
    """Basculer le statut favori d'un item archivé."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE archive SET is_favorite = NOT is_favorite WHERE id = ?", (archive_id,))
        conn.commit()

def delete_from_archive(archive_id: int) -> None:
    """Supprimer définitivement un item de l'archive."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM archive WHERE id = ?", (archive_id,))
        conn.commit()

def export_full_archive() -> list[dict]:
    """Exporter l'intégralité de l'archive."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM archive ORDER BY date_created DESC")
        return [dict(row) for row in cursor.fetchall()]

def get_cache(cache_key: str) -> str | None:
    """Récupérer le cache s'il existe et est récent."""
    with get_connection() as conn:
        cursor = conn.cursor()
        timestamp_limit = datetime.now() - timedelta(hours=CACHE_EXPIRY_HOURS)
        cursor.execute(
            "SELECT content FROM cache WHERE cache_key = ? AND timestamp > ?", 
            (cache_key, timestamp_limit)
        )
        row = cursor.fetchone()
        if row:
            return row['content']
        return None

def set_cache(cache_key: str, content: str) -> None:
    """Sauvegarder ou mettre à jour un résultat dans le cache."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO cache (cache_key, content, timestamp) 
            VALUES (?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(cache_key) DO UPDATE SET 
                content=excluded.content,
                timestamp=CURRENT_TIMESTAMP
        ''', (cache_key, content))
        conn.commit()

def cleanup_cache(days_to_keep: int = 30) -> None:
    """Removes cached items older than the specified number of days."""
    with get_connection() as conn:
        cursor = conn.cursor()
        
        # Calculate cutoff date
        cutoff_datetime = datetime.now() - timedelta(days=days_to_keep)
        
        cursor.execute("""
            DELETE FROM cache 
            WHERE timestamp < ?
        """, (cutoff_datetime,))
        conn.commit()

def clear_cache() -> None:
    """Vider toute la table cache."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cache")
        conn.commit()

def get_db_stats() -> dict:
    """Obtenir des statistiques sur l'utilisation de la base de données."""
    with get_connection() as conn:
        cursor = conn.cursor()
        stats = {}
        
        cursor.execute("SELECT COUNT(*) FROM archive WHERE content_type = 'Texte'")
        stats['textes_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM archive WHERE content_type = 'Situation'")
        stats['situations_count'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM archive WHERE content_type = 'Grille'")
        stats['grilles_count'] = cursor.fetchone()[0]
        
        # Obtenir la taille du fichier DB - on peut le faire via sqlite mais os.path est plus simple
        import os
        if os.path.exists(DB_PATH):
            stats['db_size_mb'] = round(os.path.getsize(DB_PATH) / (1024 * 1024), 2)
        else:
            stats['db_size_mb'] = 0.0
            
        return stats

# --- FONCTIONS DU CHAT ---

def create_chat_session(title: str) -> int:
    """Créer une nouvelle session de chat et retourner son ID."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_sessions (title) VALUES (?)", (title,))
        conn.commit()
        return cursor.lastrowid

def get_chat_sessions() -> list[dict]:
    """Récupérer la liste des sessions de chat, ordonnée par date de mise à jour."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM chat_sessions ORDER BY date_updated DESC")
        return [dict(row) for row in cursor.fetchall()]

def delete_chat_session(session_id: int) -> None:
    """Supprimer une session de chat et ses messages."""
    with get_connection() as conn:
        cursor = conn.cursor()
        # Les messages sont supprimés automatiquement grâce à ON DELETE CASCADE 
        # (si PRAGMA foreign_keys = ON est activé, ce qui doit être fait niveau SQLite). 
        # Pour être sûr, on supprime manuellement aussi :
        cursor.execute("DELETE FROM chat_messages WHERE session_id = ?", (session_id,))
        cursor.execute("DELETE FROM chat_sessions WHERE id = ?", (session_id,))
        conn.commit()

def add_chat_message(session_id: int, role: str, content: str) -> None:
    """Ajouter un message à une session et mettre à jour la date de la session."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_messages (session_id, role, content) VALUES (?, ?, ?)",
            (session_id, role, content)
        )
        cursor.execute(
            "UPDATE chat_sessions SET date_updated = CURRENT_TIMESTAMP WHERE id = ?",
            (session_id,)
        )
        conn.commit()

def get_chat_messages(session_id: int) -> list[dict]:
    """Récupérer tous les messages d'une session, triés par ordre chronologique."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT role, content FROM chat_messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        return [{"role": row["role"], "content": row["content"]} for row in cursor.fetchall()]
