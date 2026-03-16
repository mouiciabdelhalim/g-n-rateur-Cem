"""
backup.py — Database backup utility for the CEM Generator.

Usage:
    from backend.utils.backup import backup_database, cleanup_old_backups
    backup_database()          # creates a timestamped copy in backups/
    cleanup_old_backups(keep=5)  # keep only the 5 most recent backups
"""
import os
import shutil
import glob
import logging
from datetime import datetime
from backend.config import DB_PATH

logger = logging.getLogger(__name__)

_BACKUP_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "backups")


def backup_database(backup_dir: str = _BACKUP_DIR) -> str | None:
    """
    Create a timestamped copy of the SQLite database.

    Returns the path to the backup file, or None if the source DB doesn't exist.
    """
    if not os.path.exists(DB_PATH):
        logger.warning("backup_database: source DB not found at %s", DB_PATH)
        return None

    os.makedirs(backup_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest = os.path.join(backup_dir, f"cem_{timestamp}.db")

    try:
        shutil.copy2(DB_PATH, dest)
        logger.info("Backup created: %s", dest)
        return dest
    except OSError as exc:
        logger.error("Backup failed: %s", exc)
        return None


def cleanup_old_backups(keep: int = 5, backup_dir: str = _BACKUP_DIR) -> None:
    """
    Delete old backups, retaining only the `keep` most recent files.

    Args:
        keep: Number of most recent backups to retain (default 5).
    """
    pattern = os.path.join(backup_dir, "cem_*.db")
    backups = sorted(glob.glob(pattern), reverse=True)  # newest first
    to_delete = backups[keep:]
    for path in to_delete:
        try:
            os.remove(path)
            logger.info("Old backup removed: %s", path)
        except OSError as exc:
            logger.warning("Could not remove backup %s: %s", path, exc)
