"""
Database Manager for SnapPad

This module handles all database operations for the SnapPad application using SQLite.
It provides a clean interface for managing persistent notes storage with proper
error handling and data integrity.

Key Features:
- SQLite database management with automatic setup
- CRUD operations for notes (Create, Read, Update, Delete)
- Automatic timestamp management
- Database path management in user's AppData folder
- Transaction safety with context managers
- Type hints for better code documentation

Database Schema:
- notes table: id (PRIMARY KEY), content (TEXT), created_at (TEXT), updated_at (TEXT)

Author: SnapPad Team
Version: 1.0.0
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
import config


class DatabaseManager:
    """
    Manages SQLite database operations for SnapPad notes storage.
    
    This class provides a complete interface for managing persistent notes
    in a SQLite database. It handles database creation, table setup, and
    all CRUD operations with proper error handling and data validation.
    
    The database is stored in the user's AppData folder to ensure:
    - Persistence across application updates
    - User-specific data isolation
    - Standard Windows application data practices
    
    Database Location: %APPDATA%\SnapPad\snappad.db
    """
    
    def __init__(self):
        """
        Initialize the database manager and set up the database.
        
        This constructor:
        1. Determines the database file path
        2. Creates the application directory if needed
        3. Initializes the database with required tables
        4. Ensures the database is ready for operations
        """
        self.db_path = self._get_db_path()
        self._ensure_db_directory()
        self._initialize_database()
    
    def _get_db_path(self) -> str:
        """
        Get the full path to the SQLite database file.
        
        This method constructs the database path using:
        - Windows AppData folder (%APPDATA%)
        - Application folder name from config
        - Database filename from config
        
        Returns:
            str: Full path to the database file
            
        Example:
            C:\\Users\\Username\\AppData\\Roaming\\SnapPad\\snappad.db
        """
        # Get the user's AppData folder
        appdata = os.getenv('APPDATA', os.path.expanduser('~'))
        
        # Construct the full application directory path
        app_dir = os.path.join(appdata, config.DATABASE_FOLDER)
        
        # Return the full database file path
        return os.path.join(app_dir, config.DATABASE_FILENAME)
    
    def _ensure_db_directory(self):
        """
        Ensure the application directory exists in AppData.
        
        This method creates the application directory if it doesn't exist.
        It uses os.makedirs() which creates all necessary parent directories
        and won't raise an error if the directory already exists.
        """
        db_dir = os.path.dirname(self.db_path)
        if not os.path.exists(db_dir):
            os.makedirs(db_dir)
    
    def _initialize_database(self):
        """
        Initialize the database with required tables.
        
        This method creates the database schema if it doesn't exist.
        It uses IF NOT EXISTS to safely run on both new and existing databases.
        
        The notes table schema:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT (unique identifier)
        - content: TEXT NOT NULL (the note content)
        - created_at: TEXT DEFAULT CURRENT_TIMESTAMP (when created)
        - updated_at: TEXT DEFAULT CURRENT_TIMESTAMP (when last modified)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create the notes table with proper schema
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Commit the changes
            conn.commit()
    
    def add_note(self, content: str) -> int:
        """
        Add a new note to the database.
        
        This method creates a new note with the provided content and
        automatically sets the creation and update timestamps.
        
        Args:
            content (str): The text content of the note
            
        Returns:
            int: The ID of the newly created note
            
        Example:
            note_id = db.add_note("Remember to buy groceries")
            print(f"Note created with ID: {note_id}")
        """
        # Get the current timestamp in ISO format
        current_time = datetime.now().isoformat()
        
        # Use a context manager for automatic connection handling
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert the new note with timestamps
            cursor.execute('''
                INSERT INTO notes (content, created_at, updated_at)
                VALUES (?, ?, ?)
            ''', (content, current_time, current_time))
            
            # Commit the transaction
            conn.commit()
            
            # Return the ID of the newly created note
            return cursor.lastrowid
    
    def get_all_notes(self) -> List[Dict]:
        """
        Retrieve all notes from the database.
        
        This method fetches all notes and returns them as a list of dictionaries,
        ordered by most recently updated first. Each dictionary contains all
        note fields for easy access.
        
        Returns:
            List[Dict]: List of note dictionaries, each containing:
                - id (int): Unique note identifier
                - content (str): Note text content
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                
        Example:
            notes = db.get_all_notes()
            for note in notes:
                print(f"Note {note['id']}: {note['content']}")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query all notes ordered by most recent update first
            cursor.execute('''
                SELECT id, content, created_at, updated_at
                FROM notes
                ORDER BY updated_at DESC
            ''')
            
            # Fetch all results
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries for easier access
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
        """
        Update an existing note's content.
        
        This method updates the note content and automatically updates
        the modification timestamp. It returns a boolean indicating
        whether the update was successful.
        
        Args:
            note_id (int): The ID of the note to update
            content (str): The new content for the note
            
        Returns:
            bool: True if the note was updated successfully, False otherwise
            
        Example:
            success = db.update_note(1, "Updated note content")
            if success:
                print("Note updated successfully")
            else:
                print("Note not found or update failed")
        """
        # Get the current timestamp for the update
        current_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update the note content and timestamp
            cursor.execute('''
                UPDATE notes
                SET content = ?, updated_at = ?
                WHERE id = ?
            ''', (content, current_time, note_id))
            
            # Commit the changes
            conn.commit()
            
            # Return True if at least one row was affected
            return cursor.rowcount > 0
    
    def delete_note(self, note_id: int) -> bool:
        """
        Delete a note from the database.
        
        This method permanently removes a note from the database.
        It returns a boolean indicating whether the deletion was successful.
        
        Args:
            note_id (int): The ID of the note to delete
            
        Returns:
            bool: True if the note was deleted successfully, False otherwise
            
        Example:
            success = db.delete_note(1)
            if success:
                print("Note deleted successfully")
            else:
                print("Note not found or deletion failed")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete the note by ID
            cursor.execute('DELETE FROM notes WHERE id = ?', (note_id,))
            
            # Commit the changes
            conn.commit()
            
            # Return True if at least one row was affected
            return cursor.rowcount > 0
    
    def get_note_by_id(self, note_id: int) -> Optional[Dict]:
        """
        Retrieve a specific note by its ID.
        
        This method fetches a single note by its unique identifier.
        It returns None if the note doesn't exist.
        
        Args:
            note_id (int): The ID of the note to retrieve
            
        Returns:
            Optional[Dict]: Note dictionary if found, None otherwise
            The dictionary contains:
                - id (int): Unique note identifier
                - content (str): Note text content
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                
        Example:
            note = db.get_note_by_id(1)
            if note:
                print(f"Found note: {note['content']}")
            else:
                print("Note not found")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query for the specific note
            cursor.execute('''
                SELECT id, content, created_at, updated_at
                FROM notes
                WHERE id = ?
            ''', (note_id,))
            
            # Fetch the result
            row = cursor.fetchone()
            
            # Return the note as a dictionary if found
            if row:
                return {
                    'id': row[0],
                    'content': row[1],
                    'created_at': row[2],
                    'updated_at': row[3]
                }
            
            # Return None if note not found
            return None 