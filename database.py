"""
Database Manager for SnapPad

This module handles all database operations for the SnapPad application using SQLite.
It provides a clean interface for managing persistent notes storage with proper
error handling and data integrity.

Key Features:
- SQLite database management with automatic setup
- CRUD operations for notes (Create, Read, Update, Delete)
- Enhanced prompts management with automatic cleanup
- Automatic timestamp management
- Database path management in user's AppData folder
- Transaction safety with context managers
- Type hints for better code documentation

Database Schema:
- notes table: id (PRIMARY KEY), title (TEXT), content (TEXT), priority (INTEGER DEFAULT 1), created_at (TEXT), updated_at (TEXT)
- enhanced_prompts table: id (PRIMARY KEY), title (TEXT), content (TEXT), is_saved (BOOLEAN DEFAULT 0), created_at (TEXT), updated_at (TEXT)

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
        4. Performs any necessary migrations
        5. Ensures the database is ready for operations
        """
        self.db_path = self._get_db_path()
        self._ensure_db_directory()
        self._initialize_database()
        self._migrate_database()
    
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
        - title: TEXT (the note title)
        - content: TEXT NOT NULL (the note content)
        - priority: INTEGER DEFAULT 1 (priority level: 1=normal, 2=high, 3=urgent)
        - created_at: TEXT DEFAULT CURRENT_TIMESTAMP (when created)
        - updated_at: TEXT DEFAULT CURRENT_TIMESTAMP (when last modified)
        
        The enhanced_prompts table schema:
        - id: INTEGER PRIMARY KEY AUTOINCREMENT (unique identifier)
        - title: TEXT (the prompt title)
        - content: TEXT NOT NULL (the prompt content)
        - is_saved: BOOLEAN DEFAULT 0 (whether the prompt is saved permanently)
        - created_at: TEXT DEFAULT CURRENT_TIMESTAMP (when created)
        - updated_at: TEXT DEFAULT CURRENT_TIMESTAMP (when last modified)
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Create the notes table with proper schema including title and priority
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    priority INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create the enhanced_prompts table for storing AI-enhanced prompts
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS enhanced_prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    content TEXT NOT NULL,
                    is_saved BOOLEAN DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Commit the changes
            conn.commit()
    
    def _migrate_database(self):
        """
        Migrate existing database to add title and priority columns if they don't exist.
        
        This method handles database schema migrations for existing installations
        that might not have the title or priority columns. It checks if the columns exist
        and adds them if necessary.
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check what columns exist in notes table
            cursor.execute("PRAGMA table_info(notes)")
            columns = [column[1] for column in cursor.fetchall()]
            
            migration_needed = False
            
            # Add title column if it doesn't exist
            if 'title' not in columns:
                print("Migrating database: Adding title column to notes table")
                cursor.execute('ALTER TABLE notes ADD COLUMN title TEXT')
                
                # Update existing notes with default titles based on content
                cursor.execute('''
                    UPDATE notes 
                    SET title = CASE 
                        WHEN length(content) > 30 THEN substr(content, 1, 30) || '...'
                        ELSE content
                    END
                    WHERE title IS NULL
                ''')
                migration_needed = True
            
            # Add priority column if it doesn't exist
            if 'priority' not in columns:
                print("Migrating database: Adding priority column to notes table")
                cursor.execute('ALTER TABLE notes ADD COLUMN priority INTEGER DEFAULT 1')
                
                # Update existing notes with default priority
                cursor.execute('''
                    UPDATE notes 
                    SET priority = 1
                    WHERE priority IS NULL
                ''')
                migration_needed = True
            
            if migration_needed:
                conn.commit()
                print("Database migration completed successfully")

    # Enhanced Prompts Methods
    
    def add_enhanced_prompt(self, content: str, title: str = None) -> int:
        """
        Add a new enhanced prompt to the database.
        
        This method creates a new enhanced prompt and automatically manages
        the limit of 10 unsaved prompts by removing the oldest ones.
        
        Args:
            content (str): The enhanced prompt content
            title (str, optional): The title of the prompt. If None, generates from content.
            
        Returns:
            int: The ID of the newly created prompt
            
        Example:
            prompt_id = db.add_enhanced_prompt("Enhanced version of user's prompt", "My Enhanced Prompt")
            print(f"Enhanced prompt created with ID: {prompt_id}")
        """
        # Generate title from content if not provided
        if not title:
            title = content[:30] + "..." if len(content) > 30 else content
        
        # Get the current timestamp in ISO format
        current_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert the new enhanced prompt
            cursor.execute('''
                INSERT INTO enhanced_prompts (title, content, is_saved, created_at, updated_at)
                VALUES (?, ?, 0, ?, ?)
            ''', (title, content, current_time, current_time))
            
            # Get the ID of the newly created prompt
            prompt_id = cursor.lastrowid
            
            # Clean up old unsaved prompts (keep only the 10 most recent)
            self._cleanup_old_prompts(cursor)
            
            # Commit the transaction
            conn.commit()
            
            return prompt_id
    
    def _cleanup_old_prompts(self, cursor):
        """
        Remove old unsaved prompts to maintain the limit of 10.
        
        This method keeps only the 10 most recent unsaved prompts
        and removes older ones to prevent database bloat.
        
        Args:
            cursor: SQLite cursor for database operations
        """
        # Get all unsaved prompt IDs ordered by creation time (oldest first)
        cursor.execute('''
            SELECT id FROM enhanced_prompts 
            WHERE is_saved = 0 
            ORDER BY created_at ASC
        ''')
        
        unsaved_prompts = cursor.fetchall()
        
        # If we have more than 10 unsaved prompts, remove the oldest ones
        if len(unsaved_prompts) > 10:
            # Get IDs of prompts to delete (all except the 10 most recent)
            prompts_to_delete = unsaved_prompts[:-10]
            delete_ids = [prompt[0] for prompt in prompts_to_delete]
            
            # Delete the old prompts
            placeholders = ','.join(['?' for _ in delete_ids])
            cursor.execute(f'DELETE FROM enhanced_prompts WHERE id IN ({placeholders})', delete_ids)
    
    def get_all_enhanced_prompts(self) -> List[Dict]:
        """
        Retrieve all enhanced prompts from the database.
        
        This method fetches all enhanced prompts and returns them as a list of dictionaries,
        ordered by most recently updated first.
        
        Returns:
            List[Dict]: List of enhanced prompt dictionaries, each containing:
                - id (int): Unique prompt identifier
                - title (str): Prompt title
                - content (str): Prompt text content
                - is_saved (bool): Whether the prompt is saved permanently
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                
        Example:
            prompts = db.get_all_enhanced_prompts()
            for prompt in prompts:
                status = "Saved" if prompt['is_saved'] else "Temporary"
                print(f"Prompt {prompt['id']}: {prompt['title']} ({status})")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query all enhanced prompts ordered by most recent update first
            cursor.execute('''
                SELECT id, title, content, is_saved, created_at, updated_at
                FROM enhanced_prompts
                ORDER BY updated_at DESC
            ''')
            
            # Fetch all results
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries for easier access
            return [
                {
                    'id': row[0],
                    'title': row[1] or "Untitled",
                    'content': row[2],
                    'is_saved': bool(row[3]),
                    'created_at': row[4],
                    'updated_at': row[5]
                }
                for row in rows
            ]
    
    def get_unsaved_enhanced_prompts(self) -> List[Dict]:
        """
        Retrieve only unsaved enhanced prompts from the database.
        
        This method fetches only the temporary enhanced prompts (not saved permanently),
        ordered by most recently updated first.
        
        Returns:
            List[Dict]: List of unsaved enhanced prompt dictionaries
            
        Example:
            temp_prompts = db.get_unsaved_enhanced_prompts()
            print(f"Found {len(temp_prompts)} temporary prompts")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query only unsaved enhanced prompts
            cursor.execute('''
                SELECT id, title, content, is_saved, created_at, updated_at
                FROM enhanced_prompts
                WHERE is_saved = 0
                ORDER BY updated_at DESC
            ''')
            
            # Fetch all results
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries for easier access
            return [
                {
                    'id': row[0],
                    'title': row[1] or "Untitled",
                    'content': row[2],
                    'is_saved': bool(row[3]),
                    'created_at': row[4],
                    'updated_at': row[5]
                }
                for row in rows
            ]
    
    def update_enhanced_prompt(self, prompt_id: int, content: str = None, title: str = None, is_saved: bool = None) -> bool:
        """
        Update an existing enhanced prompt's content, title, and/or saved status.
        
        This method updates the prompt content, title, and saved status, automatically updating
        the modification timestamp.
        
        Args:
            prompt_id (int): The ID of the prompt to update
            content (str, optional): The new content for the prompt. If None, keeps existing content.
            title (str, optional): The new title for the prompt. If None, keeps existing title.
            is_saved (bool, optional): The new saved status. If None, keeps existing status.
            
        Returns:
            bool: True if the prompt was updated successfully, False otherwise
            
        Example:
            success = db.update_enhanced_prompt(1, title="New Title", is_saved=True)
            if success:
                print("Enhanced prompt updated successfully")
            else:
                print("Enhanced prompt not found or update failed")
        """
        # Get the current timestamp for the update
        current_time = datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build the update query dynamically based on provided parameters
            update_parts = []
            params = []
            
            if title is not None:
                update_parts.append('title = ?')
                params.append(title)
            
            if content is not None:
                update_parts.append('content = ?')
                params.append(content)
            
            if is_saved is not None:
                update_parts.append('is_saved = ?')
                params.append(1 if is_saved else 0)
            
            # Always update the timestamp
            update_parts.append('updated_at = ?')
            params.append(current_time)
            
            # Add the prompt_id for the WHERE clause
            params.append(prompt_id)
            
            # Execute the update
            query = f'''
                UPDATE enhanced_prompts
                SET {', '.join(update_parts)}
                WHERE id = ?
            '''
            
            cursor.execute(query, params)
            
            # Commit the changes
            conn.commit()
            
            # Return True if at least one row was affected
            return cursor.rowcount > 0
    
    def delete_enhanced_prompt(self, prompt_id: int) -> bool:
        """
        Delete an enhanced prompt from the database.
        
        This method permanently removes an enhanced prompt from the database.
        It returns a boolean indicating whether the deletion was successful.
        
        Args:
            prompt_id (int): The ID of the prompt to delete
            
        Returns:
            bool: True if the prompt was deleted successfully, False otherwise
            
        Example:
            success = db.delete_enhanced_prompt(1)
            if success:
                print("Enhanced prompt deleted successfully")
            else:
                print("Enhanced prompt not found or deletion failed")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Delete the prompt by ID
            cursor.execute('DELETE FROM enhanced_prompts WHERE id = ?', (prompt_id,))
            
            # Commit the changes
            conn.commit()
            
            # Return True if at least one row was affected
            return cursor.rowcount > 0
    
    def get_enhanced_prompt_by_id(self, prompt_id: int) -> Optional[Dict]:
        """
        Retrieve a specific enhanced prompt by its ID.
        
        This method fetches a single enhanced prompt by its unique identifier.
        It returns None if the prompt doesn't exist.
        
        Args:
            prompt_id (int): The ID of the prompt to retrieve
            
        Returns:
            Optional[Dict]: Enhanced prompt dictionary if found, None otherwise
            The dictionary contains:
                - id (int): Unique prompt identifier
                - title (str): Prompt title
                - content (str): Prompt text content
                - is_saved (bool): Whether the prompt is saved permanently
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                
        Example:
            prompt = db.get_enhanced_prompt_by_id(1)
            if prompt:
                print(f"Found prompt: {prompt['title']} (Saved: {prompt['is_saved']})")
            else:
                print("Enhanced prompt not found")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query for the specific enhanced prompt
            cursor.execute('''
                SELECT id, title, content, is_saved, created_at, updated_at
                FROM enhanced_prompts
                WHERE id = ?
            ''', (prompt_id,))
            
            # Fetch the result
            row = cursor.fetchone()
            
            # Return the prompt as a dictionary if found
            if row:
                return {
                    'id': row[0],
                    'title': row[1] or "Untitled",
                    'content': row[2],
                    'is_saved': bool(row[3]),
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            
            # Return None if prompt not found
            return None
    
    def mark_enhanced_prompt_as_saved(self, prompt_id: int) -> bool:
        """
        Mark an enhanced prompt as saved to prevent automatic cleanup.
        
        This method sets the is_saved flag to True for a specific prompt,
        which will prevent it from being automatically removed during cleanup.
        
        Args:
            prompt_id (int): The ID of the prompt to mark as saved
            
        Returns:
            bool: True if the prompt was marked as saved successfully, False otherwise
            
        Example:
            success = db.mark_enhanced_prompt_as_saved(1)
            if success:
                print("Enhanced prompt marked as saved")
            else:
                print("Enhanced prompt not found")
        """
        return self.update_enhanced_prompt(prompt_id, is_saved=True)
    
    def mark_enhanced_prompt_as_unsaved(self, prompt_id: int) -> bool:
        """
        Mark an enhanced prompt as unsaved (temporary).
        
        This method sets the is_saved flag to False for a specific prompt,
        which will make it eligible for automatic cleanup if it becomes one of the oldest.
        
        Args:
            prompt_id (int): The ID of the prompt to mark as unsaved
            
        Returns:
            bool: True if the prompt was marked as unsaved successfully, False otherwise
            
        Example:
            success = db.mark_enhanced_prompt_as_unsaved(1)
            if success:
                print("Enhanced prompt marked as temporary")
            else:
                print("Enhanced prompt not found")
        """
        return self.update_enhanced_prompt(prompt_id, is_saved=False)

    # Original Notes Methods (unchanged)
    
    def add_note(self, content: str, title: str = None, priority: int = 1) -> int:
        """
        Add a new note to the database.
        
        This method creates a new note with the provided content, title, and priority,
        automatically setting the creation and update timestamps.
        
        Args:
            content (str): The text content of the note
            title (str, optional): The title of the note. If None, generates from content.
            priority (int, optional): Priority level (1=normal, 2=high, 3=urgent). Defaults to 1.
            
        Returns:
            int: The ID of the newly created note
            
        Example:
            note_id = db.add_note("Remember to buy groceries", "Shopping List", 2)
            print(f"Note created with ID: {note_id}")
        """
        # Generate title from content if not provided
        if not title:
            title = content[:30] + "..." if len(content) > 30 else content
        
        # Validate priority (ensure it's between 1 and 3)
        priority = max(1, min(3, priority))
        
        # Get the current timestamp in ISO format
        current_time = datetime.now().isoformat()
        
        # Use a context manager for automatic connection handling
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Insert the new note with title, priority, and timestamps
            cursor.execute('''
                INSERT INTO notes (title, content, priority, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (title, content, priority, current_time, current_time))
            
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
                - title (str): Note title
                - content (str): Note text content
                - priority (int): Priority level (1=normal, 2=high, 3=urgent)
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                
        Example:
            notes = db.get_all_notes()
            for note in notes:
                print(f"Note {note['id']}: {note['title']} (Priority: {note['priority']}) - {note['content']}")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query all notes ordered by most recent update first (keeping original sorting)
            cursor.execute('''
                SELECT id, title, content, priority, created_at, updated_at
                FROM notes
                ORDER BY updated_at DESC
            ''')
            
            # Fetch all results
            rows = cursor.fetchall()
            
            # Convert rows to dictionaries for easier access
            return [
                {
                    'id': row[0],
                    'title': row[1] or "Untitled",  # Fallback for null titles
                    'content': row[2],
                    'priority': row[3] if row[3] is not None else 1,  # Fallback for null priorities
                    'created_at': row[4],
                    'updated_at': row[5]
                }
                for row in rows
            ]
    
    def update_note(self, note_id: int, content: str, title: str = None, priority: int = None) -> bool:
        """
        Update an existing note's content, title, and/or priority.
        
        This method updates the note content, title, and priority, automatically updating
        the modification timestamp. It returns a boolean indicating
        whether the update was successful.
        
        Args:
            note_id (int): The ID of the note to update
            content (str): The new content for the note
            title (str, optional): The new title for the note. If None, keeps existing title.
            priority (int, optional): The new priority level. If None, keeps existing priority.
            
        Returns:
            bool: True if the note was updated successfully, False otherwise
            
        Example:
            success = db.update_note(1, "Updated note content", "New Title", 3)
            if success:
                print("Note updated successfully")
            else:
                print("Note not found or update failed")
        """
        # Get the current timestamp for the update
        current_time = datetime.now().isoformat()
        
        # Validate priority if provided
        if priority is not None:
            priority = max(1, min(3, priority))
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if title is not None and priority is not None:
                # Update content, title, priority and timestamp
                cursor.execute('''
                    UPDATE notes
                    SET title = ?, content = ?, priority = ?, updated_at = ?
                    WHERE id = ?
                ''', (title, content, priority, current_time, note_id))
            elif title is not None:
                # Update content, title and timestamp
                cursor.execute('''
                    UPDATE notes
                    SET title = ?, content = ?, updated_at = ?
                    WHERE id = ?
                ''', (title, content, current_time, note_id))
            elif priority is not None:
                # Update content, priority and timestamp
                cursor.execute('''
                    UPDATE notes
                    SET content = ?, priority = ?, updated_at = ?
                    WHERE id = ?
                ''', (content, priority, current_time, note_id))
            else:
                # Update only content and timestamp
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
                - title (str): Note title
                - content (str): Note text content
                - priority (int): Priority level (1=normal, 2=high, 3=urgent)
                - created_at (str): Creation timestamp
                - updated_at (str): Last update timestamp
                
        Example:
            note = db.get_note_by_id(1)
            if note:
                print(f"Found note: {note['title']} (Priority: {note['priority']}) - {note['content']}")
            else:
                print("Note not found")
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Query for the specific note
            cursor.execute('''
                SELECT id, title, content, priority, created_at, updated_at
                FROM notes
                WHERE id = ?
            ''', (note_id,))
            
            # Fetch the result
            row = cursor.fetchone()
            
            # Return the note as a dictionary if found
            if row:
                return {
                    'id': row[0],
                    'title': row[1] or "Untitled",  # Fallback for null titles
                    'content': row[2],
                    'priority': row[3] if row[3] is not None else 1,  # Fallback for null priorities
                    'created_at': row[4],
                    'updated_at': row[5]
                }
            
            # Return None if note not found
            return None 