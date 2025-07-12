import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import config


class DatabaseManager:
    """Manages SQLite database operations for SnapPad."""
    
    def __init__(self):
        self.db_path = self._get_db_path()
        self._ensure_db_directory()
        self._initialize_database()
    
    def _get_db_path(self) -> str:
        """Get the path to the SQLite database file."""
        appdata = os.getenv('APPDATA', os.path.expanduser('~'))
        app_dir = os.path.join(appdata, config.DATABASE_FOLDER)
        return os.path.join(app_dir, config.DATABASE_FILENAME)
    
    def _ensure_db_directory(self):
        """Ensure the application directory exists."""
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _initialize_database(self):
        """Initialize the database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
    
    def add_note(self, content: str) -> int:
        """Add a new note to the database."""
        current_time = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO notes (content, created_at, updated_at)
                VALUES (?, ?, ?)
            ''', (content, current_time, current_time))
            conn.commit()
            return cursor.lastrowid
    
    def get_all_notes(self) -> List[Dict]:
        """Get all notes from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, content, created_at, updated_at
                FROM notes
                ORDER BY updated_at DESC
            ''')
            rows = cursor.fetchall()
            return [
                {
                    'id': row[0],
                    'content': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                }
                for row in rows
            ]
    
    def update_note(self, note_id: int, content: str) -> bool:
        """Update an existing note."""
        current_time = datetime.now().isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notes
                SET content = ?, updated_at = ?
                WHERE id = ?
            ''', (content, current_time, note_id))
            conn.commit()
            return cursor.rowcount > 0
    
    def delete_note(self, note_id: int) -> bool:
        """Delete a note from the database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_note_by_id(self, note_id: int) -> Optional[Dict]:
        """Get a specific note by ID."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT id, content, created_at, updated_at
                FROM notes
                WHERE id = ?
            ''', (note_id,))
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'content': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                }
        return None 