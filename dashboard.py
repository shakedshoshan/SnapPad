"""
Dashboard UI for SnapPad

This module contains the main user interface for the SnapPad application using PyQt6.
It provides a modern, always-on-top dashboard that displays clipboard history and
manages persistent notes with an intuitive interface.

Key Features:
- Always-on-top window positioned on the right side of the screen
- Real-time clipboard history display with clickable items
- Notes management with inline editing capabilities
- Modern UI with hover effects and smooth interactions
- Thread-safe operations with signal-slot communication
- Responsive design that adapts to different screen sizes
- Integrated search and management tools

UI Components:
- ClickableLabel: Custom label widget for interactive clipboard items
- EditableNoteWidget: Complex widget for displaying and editing notes
- Dashboard: Main window class that orchestrates the entire interface

The dashboard follows PyQt6 best practices with proper signal-slot communication
and thread-safe operations for background task integration.

Author: SnapPad Team
Version: 1.0.0
"""

import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QListWidget, QListWidgetItem, 
                             QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                             QSplitter, QFrame, QScrollArea, QComboBox)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QAction, QShortcut, QKeySequence
from typing import List, Dict, Optional, Callable
import threading
from datetime import datetime
import config


class ClickableLabel(QLabel):
    """
    A clickable label widget that emits signals when clicked.
    
    This custom QLabel provides clickable functionality for clipboard history items.
    When clicked, it emits a signal with the label's text content, allowing the
    parent widget to handle the click event (typically to copy the text back
    to the clipboard).
    
    Features:
    - Hover effects with color changes
    - Word wrapping for long text
    - Custom styling with borders and padding
    - Click detection and signal emission
    - Pointer cursor on hover
    """
    
    # Signal emitted when the label is clicked, passing the text content
    clicked = pyqtSignal(str)
    
    def __init__(self, text: str, *args, **kwargs):
        """
        Initialize the clickable label.
        
        Args:
            text (str): The text content to display in the label.
            *args: Additional positional arguments passed to QLabel.
            **kwargs: Additional keyword arguments passed to QLabel.
        """
        super().__init__(text, *args, **kwargs)
        
        # Enable word wrapping for long text
        self.setWordWrap(True)
        
        # Apply custom styling
        self.setStyleSheet("""
            QLabel {
                background: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                padding: 6px;
                margin: 2px;
                color: #333333;
                font-size: 12px;
            }
            QLabel:hover {
                background: #f5f5f5;
                border-color: #4a90e2;
            }
        """)
        
        # Set cursor to pointer to indicate clickability
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        """
        Handle mouse press events to detect clicks.
        
        This method is called when the user clicks on the label. It emits
        the clicked signal with the label's text content if the left mouse
        button was pressed.
        
        Args:
            event: The mouse press event containing button and position information.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # Emit the clicked signal with the label's text
            self.clicked.emit(self.text())
        
        # Call the parent implementation to ensure proper event handling
        super().mousePressEvent(event)


class EditableNoteWidget(QWidget):
    """
    A complex widget for displaying and editing notes with inline editing capabilities.
    
    This widget provides a complete note management interface including:
    - Display mode: Shows note title, content, and date info with action buttons
    - Edit mode: Provides text editing for both title and content with save/cancel options
    - Action buttons: Edit, delete, copy, and save functionality
    - Visual feedback: Hover effects and state transitions
    - Signal communication: Emits signals for parent coordination
    
    The widget automatically switches between display and edit modes,
    providing a seamless user experience for note management.
    """
    
    # Signals for communicating with the parent widget
    note_updated = pyqtSignal(int, str, str, int)  # Emitted when note is updated (id, content, title, priority)
    note_deleted = pyqtSignal(int)       # Emitted when note is deleted
    note_copied = pyqtSignal(str)        # Emitted when note content is copied
    
    def __init__(self, note_data: Dict, parent=None):
        """
        Initialize the editable note widget.
        
        Args:
            note_data (Dict): Dictionary containing note information with keys:
                            - id: Unique note identifier
                            - title: Note title
                            - content: Note text content
                            - priority: Priority level (1=normal, 2=high, 3=urgent)
                            - created_at: Creation timestamp
                            - updated_at: Last update timestamp
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        # Store note data
        self.note_data = note_data
        
        # Track editing state
        self.is_editing = False
        
        # Set up the user interface
        self.setup_ui()
    
    def setup_ui(self):
        """
        Set up the user interface for the note widget.
        
        This method creates and configures all UI elements including:
        - Main container with styling
        - Title display and editing
        - Content display and editing
        - Date information
        - Action buttons (Edit, Delete, Copy, Save, Cancel)
        - Layout management and styling
        """
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Create main container frame with border and styling
        self.container = QFrame()
        self.container.setFrameStyle(QFrame.Shape.Box)
        self.container.setStyleSheet("""
            QFrame {
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                margin: 1px;
                background: #ffffff;
            }
            QFrame:hover {
                border-color: #d0d0d0;
            }
        """)
        
        # Container layout with proper spacing
        container_layout = QVBoxLayout()
        container_layout.setSpacing(4)
        container_layout.setContentsMargins(6, 6, 6, 6)
        
        # Header layout for title and priority
        header_layout = QHBoxLayout()
        header_layout.setSpacing(8)
        
        # Title display label (shown in display mode)
        self.title_display_label = QLabel(self.note_data['title'])
        self.title_display_label.setWordWrap(True)
        self.title_display_label.setStyleSheet("""
            QLabel {
                border: none; 
                background: transparent; 
                padding: 2px;
                color: #2c3e50;
                font-size: 14px;
                font-weight: bold;
                line-height: 1.2;
            }
        """)
        
        # Priority display label (shown in display mode)
        self.priority_display_label = QLabel(self._get_priority_text(self.note_data['priority']))
        self.priority_display_label.setStyleSheet(f"""
            QLabel {{
                border: none; 
                background: {self._get_priority_color(self.note_data['priority'])}; 
                padding: 2px 6px;
                color: white;
                font-size: 10px;
                font-weight: bold;
                border-radius: 8px;
                max-width: 50px;
            }}
        """)
        
        header_layout.addWidget(self.title_display_label)
        header_layout.addStretch()
        header_layout.addWidget(self.priority_display_label)
        
        # Edit mode header layout
        edit_header_layout = QHBoxLayout()
        edit_header_layout.setSpacing(8)
        
        # Title editor (shown in edit mode)
        self.title_edit = QLineEdit()
        self.title_edit.setText(self.note_data['title'])
        self.title_edit.setPlaceholderText("Note title...")
        self.title_edit.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px;
                font-size: 14px;
                font-weight: bold;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        
        # Priority editor (shown in edit mode)
        self.priority_edit = QComboBox()
        self.priority_edit.addItems(["1", "2", "3"])
        self.priority_edit.setCurrentIndex(self.note_data['priority'] - 1)  # Convert to 0-based index
        self.priority_edit.setMaximumWidth(80)
        self.priority_edit.setStyleSheet("""
            QComboBox {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QComboBox:focus {
                border-color: #4a90e2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        
        edit_header_layout.addWidget(self.title_edit)
        edit_header_layout.addWidget(self.priority_edit)
        
        # Create containers for the headers
        self.display_header_widget = QWidget()
        self.display_header_widget.setLayout(header_layout)
        
        self.edit_header_widget = QWidget()
        self.edit_header_widget.setLayout(edit_header_layout)
        self.edit_header_widget.hide()  # Hidden by default
        
        # Note content display label (shown in display mode)
        self.content_display_label = QLabel(self.note_data['content'])
        self.content_display_label.setWordWrap(True)
        self.content_display_label.setStyleSheet("""
            QLabel {
                border: none; 
                background: transparent; 
                padding: 4px;
                color: #333333;
                font-size: 13px;
                line-height: 1.3;
            }
        """)
        
        # Note content text editor (shown in edit mode)
        self.content_edit_text = QTextEdit()
        self.content_edit_text.setPlainText(self.note_data['content'])
        self.content_edit_text.setMaximumHeight(60)  # Compact height for better UI
        self.content_edit_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                padding: 4px;
                font-size: 13px;
                background-color: #ffffff;
                color: #333333;
            }
            QTextEdit:focus {
                border-color: #4a90e2;
            }
        """)
        self.content_edit_text.hide()  # Hidden by default
        
        # Date information label
        self.date_label = QLabel(self._format_date_info())
        self.date_label.setStyleSheet("""
            QLabel {
                border: none; 
                background: transparent; 
                padding: 2px;
                color: #7f8c8d;
                font-size: 10px;
                font-style: italic;
            }
        """)
        
        # Button container layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)
        
        # Edit button - switches to edit mode
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.setMaximumWidth(50)
        self.edit_btn.setMaximumHeight(24)
        self.edit_btn.clicked.connect(self.toggle_edit_mode)
        self.edit_btn.setStyleSheet("""
            QPushButton {
                background: #4a90e2;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #357abd;
            }
        """)
        
        # Delete button - removes the note
        self.delete_btn = QPushButton("Del")
        self.delete_btn.setMaximumWidth(40)
        self.delete_btn.setMaximumHeight(24)
        self.delete_btn.clicked.connect(self.delete_note)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        
        # Save button - saves changes (hidden in display mode)
        self.save_btn = QPushButton("Save")
        self.save_btn.setMaximumWidth(50)
        self.save_btn.setMaximumHeight(24)
        self.save_btn.clicked.connect(self.save_note)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        self.save_btn.hide()  # Hidden by default
        
        # Cancel button - cancels editing (hidden in display mode)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setMaximumWidth(55)
        self.cancel_btn.setMaximumHeight(24)
        self.cancel_btn.clicked.connect(self.cancel_edit)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        self.cancel_btn.hide()  # Hidden by default
        
        # Copy button - copies note content to clipboard
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setMaximumWidth(50)
        self.copy_btn.setMaximumHeight(24)
        self.copy_btn.clicked.connect(self.copy_note)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background: #8e44ad;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 4px 8px;
                font-size: 11px;
            }
            QPushButton:hover {
                background: #7d3c98;
            }
        """)
        
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.save_btn)
        button_layout.addWidget(self.cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(self.copy_btn)
        
        # Add widgets to container layout
        container_layout.addWidget(self.display_header_widget)
        container_layout.addWidget(self.edit_header_widget)
        container_layout.addWidget(self.content_display_label)
        container_layout.addWidget(self.content_edit_text)
        container_layout.addWidget(self.date_label)
        container_layout.addLayout(button_layout)
        
        # Set layout for the container frame
        self.container.setLayout(container_layout)
        
        # Add container to the main layout
        layout.addWidget(self.container)
        
        # Set the main layout for the widget
        self.setLayout(layout)
    
    def _format_date_info(self) -> str:
        """
        Format the date information for display.
        
        Returns:
            str: Formatted date string showing creation and update times
        """
        try:
            # Parse the ISO format timestamps
            created_dt = datetime.fromisoformat(self.note_data['created_at'].replace('Z', '+00:00'))
            updated_dt = datetime.fromisoformat(self.note_data['updated_at'].replace('Z', '+00:00'))
            
            # Format for display
            created_str = created_dt.strftime("%m/%d/%Y %H:%M")
            updated_str = updated_dt.strftime("%m/%d/%Y %H:%M")
            
            # Check if the note was updated after creation
            if created_str == updated_str:
                return f"Created: {created_str}"
            else:
                return f"Created: {created_str} | Updated: {updated_str}"
                
        except (ValueError, KeyError):
            # Fallback for malformed dates
            return "Date information unavailable"
    
    def _get_priority_text(self, priority: int) -> str:
        """
        Get the display text for a priority level.
        
        Args:
            priority (int): Priority level (1-3)
            
        Returns:
            str: Display text for the priority
        """
        return str(priority) if priority in [1, 2, 3] else "1"
    
    def _get_priority_color(self, priority: int) -> str:
        """
        Get the display color for a priority level.
        
        Args:
            priority (int): Priority level (1-3)
            
        Returns:
            str: CSS color code for the priority
        """
        color_map = {1: "#95a5a6", 2: "#f39c12", 3: "#e74c3c"}
        return color_map.get(priority, "#95a5a6")
    
    def toggle_edit_mode(self):
        """
        Toggle between display and edit mode for the note widget.
        
        This method handles the state transitions for the note widget,
        showing the editors and hiding the display headers, and vice versa.
        It also manages the visibility of action buttons (Edit, Delete, Save, Cancel)
        based on the current mode.
        """
        self.is_editing = not self.is_editing
        
        if self.is_editing:
            self.display_header_widget.hide()
            self.content_display_label.hide()
            self.edit_header_widget.show()
            self.content_edit_text.show()
            self.edit_btn.hide()
            self.delete_btn.hide()
            self.save_btn.show()
            self.cancel_btn.show()
            self.title_edit.setFocus()
        else:
            self.display_header_widget.show()
            self.content_display_label.show()
            self.edit_header_widget.hide()
            self.content_edit_text.hide()
            self.edit_btn.show()
            self.delete_btn.show()
            self.save_btn.hide()
            self.cancel_btn.hide()
    
    def save_note(self):
        """
        Save the edited note title, content, and priority to the database.
        
        This method is called when the user clicks the "Save" button in edit mode.
        It retrieves the new title, content, and priority from the editors, updates the note data,
        and emits a signal to notify the parent widget.
        """
        new_title = self.title_edit.text().strip()
        new_content = self.content_edit_text.toPlainText().strip()
        new_priority = self.priority_edit.currentIndex() + 1  # Convert from 0-based to 1-based
        
        # Ensure we have at least a title or content
        if new_content or new_title:
            # Use default values if either is empty
            if not new_title:
                new_title = new_content[:30] + "..." if len(new_content) > 30 else new_content
            if not new_content:
                new_content = new_title
                
            self.note_data['title'] = new_title
            self.note_data['content'] = new_content
            self.note_data['priority'] = new_priority
            
            # Update display elements
            self.title_display_label.setText(new_title)
            self.content_display_label.setText(new_content)
            self.priority_display_label.setText(self._get_priority_text(new_priority))
            self.priority_display_label.setStyleSheet(f"""
                QLabel {{
                    border: none; 
                    background: {self._get_priority_color(new_priority)}; 
                    padding: 2px 6px;
                    color: white;
                    font-size: 10px;
                    font-weight: bold;
                    border-radius: 8px;
                    max-width: 50px;
                }}
            """)
            
            self.note_updated.emit(self.note_data['id'], new_content, new_title, new_priority)
            self.toggle_edit_mode()
    
    def cancel_edit(self):
        """
        Cancel editing and revert changes for the note widget.
        
        This method is called when the user clicks the "Cancel" button in edit mode.
        It restores the original title, content, and priority from the note data and reverts to display mode.
        """
        self.title_edit.setText(self.note_data['title'])
        self.content_edit_text.setPlainText(self.note_data['content'])
        self.priority_edit.setCurrentIndex(self.note_data['priority'] - 1)  # Convert to 0-based index
        self.toggle_edit_mode()
    
    def delete_note(self):
        """
        Delete the note from the database after confirmation.
        
        This method is called when the user clicks the "Delete" button.
        It shows a confirmation dialog and, if confirmed, emits a signal to
        notify the parent widget to delete the note from the database.
        """
        reply = QMessageBox.question(
            self, 
            "Delete Note", 
            "Are you sure you want to delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.note_deleted.emit(self.note_data['id'])
    
    def copy_note(self):
        """
        Copy the current note content to the clipboard.
        
        This method is called when the user clicks the "Copy" button.
        It emits a signal to notify the parent widget to copy the content
        to the clipboard.
        """
        self.note_copied.emit(self.note_data['content'])


class NotesWindow(QMainWindow):
    """
    A dedicated window for displaying all notes in a larger, more readable format.
    
    This window provides:
    - Centered positioning on screen
    - Larger display area for better readability
    - All the same functionality as the dashboard notes (edit, delete, copy)
    - Auto-refresh when notes are updated
    """
    
    def __init__(self, parent=None):
        """
        Initialize the notes window.
        
        Args:
            parent: Parent widget (usually the main Dashboard)
        """
        super().__init__(parent)
        self.parent_dashboard = parent
        self.database_manager = None
        
        # Setup UI and window properties
        self.setup_ui()
        self.setup_window_properties()
    
    def setup_ui(self):
        """
        Set up the user interface for the notes window.
        """
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set window styling
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Header with title and close button
        header_layout = QHBoxLayout()
        
        # title_label = QLabel("📝 All Notes")
        # title_label.setStyleSheet("""
        #     QLabel {
        #         font-size: 18px; 
        #         font-weight: bold; 
        #         color: #2c3e50;
        #         background: transparent;
        #     }
        # """)
        
        # close_button = QPushButton("×")
        # close_button.setMaximumSize(30, 30)
        # close_button.setStyleSheet("""
        #     QPushButton {
        #         background: #e74c3c;
        #         color: white;
        #         border: none;
        #         border-radius: 15px;
        #         font-size: 16px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background: #c0392b;
        #     }
        # """)
        # close_button.clicked.connect(self.close)
        
        # header_layout.addWidget(title_label)
        header_layout.addStretch()
        # header_layout.addWidget(close_button)
        
        # Notes container
        notes_container = QFrame()
        notes_container.setFrameStyle(QFrame.Shape.Box)
        notes_container.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
                padding: 10px;
            }
        """)
        
        container_layout = QVBoxLayout()
        container_layout.setSpacing(10)
        container_layout.setContentsMargins(10, 10, 10, 10)
        
        # Notes scroll area
        self.notes_scroll = QScrollArea()
        self.notes_scroll.setWidgetResizable(True)
        self.notes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.notes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.notes_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f1f3f4;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
        """)
        
        self.notes_content = QWidget()
        self.notes_content_layout = QVBoxLayout()
        self.notes_content_layout.setSpacing(10)
        self.notes_content_layout.setContentsMargins(10, 10, 10, 10)
        self.notes_content.setLayout(self.notes_content_layout)
        self.notes_scroll.setWidget(self.notes_content)
        
        container_layout.addWidget(self.notes_scroll)
        notes_container.setLayout(container_layout)
        
        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(notes_container)
        
        central_widget.setLayout(main_layout)
    
    def setup_window_properties(self):
        """
        Configure window properties for the notes window.
        """
        self.setWindowTitle("SnapPad - All Notes")
        self.setMinimumSize(600, 500)
        self.resize(800, 600)
        
        # Center window on screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Set window flags
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
    
    def set_database_manager(self, database_manager):
        """
        Set the database manager for the notes window.
        
        Args:
            database_manager: The database manager instance
        """
        self.database_manager = database_manager
        self.refresh_notes()
    
    def refresh_notes(self):
        """
        Refresh the display of notes in the window.
        """
        if not self.database_manager:
            return
        
        # Clear existing notes
        for i in reversed(range(self.notes_content_layout.count())):
            child = self.notes_content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add current notes
        notes = self.database_manager.get_all_notes()
        
        if not notes:
            no_notes_label = QLabel("No notes yet. Add your first note in the main dashboard!")
            no_notes_label.setStyleSheet("""
                QLabel {
                    color: #7f8c8d; 
                    font-style: italic; 
                    font-size: 14px;
                    padding: 20px;
                    background: transparent;
                    text-align: center;
                }
            """)
            no_notes_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.notes_content_layout.addWidget(no_notes_label)
        else:
            for note in notes:
                note_widget = EditableNoteWidget(note)
                note_widget.note_updated.connect(self.update_note)
                note_widget.note_deleted.connect(self.delete_note)
                note_widget.note_copied.connect(self.copy_to_clipboard)
                self.notes_content_layout.addWidget(note_widget)
        
        # Add stretch to push items to top
        self.notes_content_layout.addStretch()
    
    def update_note(self, note_id: int, content: str, title: str, priority: int):
        """
        Update a note in the database and refresh parent dashboard.
        
        Args:
            note_id (int): The unique identifier of the note to update
            content (str): The new content for the note
            title (str): The new title for the note
            priority (int): The new priority level for the note
        """
        if self.database_manager:
            self.database_manager.update_note(note_id, content, title, priority)
            # Refresh parent dashboard if available
            if self.parent_dashboard:
                self.parent_dashboard.refresh_notes()
    
    def delete_note(self, note_id: int):
        """
        Delete a note from the database and refresh displays.
        
        Args:
            note_id (int): The unique identifier of the note to delete
        """
        if self.database_manager:
            self.database_manager.delete_note(note_id)
            self.refresh_notes()
            # Refresh parent dashboard if available
            if self.parent_dashboard:
                self.parent_dashboard.refresh_notes()
    
    def copy_to_clipboard(self, text: str):
        """
        Copy text to clipboard using parent dashboard's clipboard manager.
        
        Args:
            text (str): The text content to copy
        """
        if self.parent_dashboard and self.parent_dashboard.clipboard_manager:
            self.parent_dashboard.clipboard_manager.copy_to_clipboard(text)


class Dashboard(QMainWindow):
    """
    Main dashboard window for SnapPad.
    
    This class manages the overall dashboard interface, including:
    - Clipboard history display
    - Notes management
    - User input for new notes
    - Signal communication with managers (clipboard, database)
    - Window positioning and visibility
    - Thread-safe operations for hotkey triggers
    """
    
    # Define signals for thread-safe communication
    toggle_visibility_signal = pyqtSignal()
    add_note_from_clipboard_signal = pyqtSignal()
    
    def __init__(self):
        """
        Initialize the dashboard window.
        
        This constructor sets up the main window, manages managers,
        and connects signals to their respective slots.
        """
        super().__init__()
        
        # Initialize managers
        self.clipboard_manager = None
        self.database_manager = None
        
        # Initialize notes window reference
        self.notes_window = None
        
        # Set up the user interface
        self.setup_ui()
        
        # Configure window properties
        self.setup_window_properties()
        
        # Connect signals to their respective slots
        self.toggle_visibility_signal.connect(self.toggle_visibility)
        self.add_note_from_clipboard_signal.connect(self.add_note_from_clipboard)
        
        # Timer for refreshing clipboard history
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_clipboard_history)
        self.refresh_timer.start(config.REFRESH_INTERVAL)  # Refresh based on config
    
    def setup_ui(self):
        """
        Set up the user interface for the dashboard.
        
        This method creates and configures all UI elements including:
        - Main window layout
        - Header with title and close button
        - Splitter for resizable sections (Clipboard History, Notes)
        - Clipboard history display area
        - Notes input area and list
        - Styling and layout management
        """
        # Central widget for the main window
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set main window background
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
            }
        """)
        
        # Main layout - reduced margins
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)  # Reduced from 15
        main_layout.setSpacing(8)  # Reduced from 15
        
        # # Title
        # title_label = QLabel("📋 SnapPad")
        # title_label.setStyleSheet("""
        #     QLabel {
        #         font-size: 16px; 
        #         font-weight: bold; 
        #         color: #2c3e50;
        #         margin-bottom: 4px;
        #         background: transparent;
        #     }
        # """)
        # title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # # Close button - smaller
        # close_button = QPushButton("×")
        # close_button.setMaximumSize(24, 24)  # Reduced from 35x35
        # close_button.setStyleSheet("""
        #     QPushButton {
        #         background: #e74c3c;
        #         color: white;
        #         border: none;
        #         border-radius: 12px;
        #         font-size: 14px;
        #         font-weight: bold;
        #     }
        #     QPushButton:hover {
        #         background: #c0392b;
        #     }
        # """)
        # close_button.clicked.connect(self.hide)
        
        # Header layout
        header_layout = QHBoxLayout()
        # header_layout.addWidget(title_label)
        header_layout.addStretch()
        # header_layout.addWidget(close_button)
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Orientation.Vertical)
        splitter.setStyleSheet("""
            QSplitter::handle {
                background-color: #bdc3c7;
                border-radius: 1px;
                margin: 1px;
            }
            QSplitter::handle:hover {
                background-color: #95a5a6;
            }
        """)
        
        # Clipboard History Section
        clipboard_frame = QFrame()
        clipboard_frame.setFrameStyle(QFrame.Shape.Box)
        clipboard_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: #ffffff;
                padding: 4px;
            }
        """)
        clipboard_layout = QVBoxLayout()
        clipboard_layout.setSpacing(6)  # Reduced from 10
        clipboard_layout.setContentsMargins(6, 6, 6, 6)
        
        clipboard_title = QLabel("📋 Clipboard History")
        clipboard_title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 13px;
                color: #2c3e50;
                margin-bottom: 2px;
                background: transparent;
            }
        """)
        clipboard_layout.addWidget(clipboard_title)
        
        self.clipboard_scroll = QScrollArea()
        self.clipboard_scroll.setWidgetResizable(True)
        self.clipboard_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.clipboard_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.clipboard_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f1f3f4;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
        """)
        
        self.clipboard_content = QWidget()
        self.clipboard_content_layout = QVBoxLayout()
        self.clipboard_content_layout.setSpacing(2)  # Reduced spacing
        self.clipboard_content_layout.setContentsMargins(2, 2, 2, 2)
        self.clipboard_content.setLayout(self.clipboard_content_layout)
        self.clipboard_scroll.setWidget(self.clipboard_content)
        
        clipboard_layout.addWidget(self.clipboard_scroll)
        clipboard_frame.setLayout(clipboard_layout)
        
        # Notes Section
        notes_frame = QFrame()
        notes_frame.setFrameStyle(QFrame.Shape.Box)
        notes_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: #ffffff;
                padding: 4px;
            }
        """)
        notes_layout = QVBoxLayout()
        notes_layout.setSpacing(6)  # Reduced from 10
        notes_layout.setContentsMargins(6, 6, 6, 6)
        
        # Notes header with title and Open button
        notes_header_layout = QHBoxLayout()
        notes_header_layout.setSpacing(10)
        
        notes_title = QLabel("📝 Notes")
        notes_title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 13px;
                color: #2c3e50;
                margin-bottom: 2px;
                background: transparent;
            }
        """)
        
        # Open Notes button
        self.open_notes_btn = QPushButton("Open")
        self.open_notes_btn.setMaximumWidth(60)
        self.open_notes_btn.setMaximumHeight(24)
        self.open_notes_btn.clicked.connect(self.open_all_notes)
        self.open_notes_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
        """)
        
        notes_header_layout.addWidget(notes_title)
        notes_header_layout.addStretch()
        notes_header_layout.addWidget(self.open_notes_btn)
        
        notes_layout.addLayout(notes_header_layout)
        
        # Add note input section
        add_note_layout = QVBoxLayout()
        add_note_layout.setSpacing(4)
        
        # Title and priority input layout
        title_priority_layout = QHBoxLayout()
        title_priority_layout.setSpacing(6)
        
        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Note title (optional)...")
        self.title_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
                font-weight: bold;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        self.title_input.returnPressed.connect(self.add_note)
        
        # Priority input
        self.priority_input = QComboBox()
        self.priority_input.addItems(["1", "2", "3"])
        self.priority_input.setCurrentIndex(0)  # Default to 1
        self.priority_input.setMaximumWidth(80)
        self.priority_input.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QComboBox:focus {
                border-color: #4a90e2;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: none;
                border: none;
            }
        """)
        
        title_priority_layout.addWidget(self.title_input)
        title_priority_layout.addWidget(self.priority_input)
        
        # Content input with add button layout
        content_add_layout = QHBoxLayout()
        content_add_layout.setSpacing(6)
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Enter note content...")
        self.note_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 13px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        self.note_input.returnPressed.connect(self.add_note)
        
        add_note_btn = QPushButton("Add")
        add_note_btn.setMaximumWidth(60)  # Smaller button
        add_note_btn.setMaximumHeight(28)
        add_note_btn.clicked.connect(self.add_note)
        add_note_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        content_add_layout.addWidget(self.note_input)
        content_add_layout.addWidget(add_note_btn)
        
        add_note_layout.addLayout(title_priority_layout)
        add_note_layout.addLayout(content_add_layout)
        notes_layout.addLayout(add_note_layout)
        
        # Notes scroll area
        self.notes_scroll = QScrollArea()
        self.notes_scroll.setWidgetResizable(True)
        self.notes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.notes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.notes_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
            QScrollBar:vertical {
                background: #f1f3f4;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
        """)
        
        self.notes_content = QWidget()
        self.notes_content_layout = QVBoxLayout()
        self.notes_content_layout.setSpacing(2)  # Reduced spacing
        self.notes_content_layout.setContentsMargins(2, 2, 2, 2)
        self.notes_content.setLayout(self.notes_content_layout)
        self.notes_scroll.setWidget(self.notes_content)
        
        notes_layout.addWidget(self.notes_scroll)
        notes_frame.setLayout(notes_layout)
        
        # Add frames to splitter
        splitter.addWidget(clipboard_frame)
        splitter.addWidget(notes_frame)
        splitter.setSizes([200, 300])  # Initial sizes
        
        # Add everything to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(splitter)
        
        central_widget.setLayout(main_layout)
    
    def setup_window_properties(self):
        """
        Configure window properties for the dashboard.
        
        This method sets the window title, size, position, and window flags.
        It ensures the window is positioned on the right side of the screen
        and always stays on top if configured.
        """
        self.setWindowTitle("SnapPad")
        self.setFixedSize(config.DASHBOARD_WIDTH, config.DASHBOARD_HEIGHT)
        
        # Position window on the right side of the screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        x = screen_geometry.width() - self.width() - config.DASHBOARD_POSITION_X_OFFSET
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Keep window always on top based on config
        flags = Qt.WindowType.Tool
        if config.DASHBOARD_ALWAYS_ON_TOP:
            flags |= Qt.WindowType.WindowStaysOnTopHint
        self.setWindowFlags(flags)
        
        # Hide initially
        self.hide()
    
    def set_managers(self, clipboard_manager, database_manager):
        """
        Set the clipboard and database managers for the dashboard.
        
        This method assigns the provided managers to the dashboard's attributes
        and triggers a refresh of the notes display.
        
        Args:
            clipboard_manager: The manager responsible for clipboard operations.
            database_manager: The manager responsible for managing notes.
        """
        self.clipboard_manager = clipboard_manager
        self.database_manager = database_manager
        
        # Load initial notes
        self.refresh_notes()
    
    def refresh_clipboard_history(self):
        """
        Refresh the display of clipboard history items.
        
        This method clears existing items and repopulates the clipboard history
        display with the latest history from the clipboard manager.
        """
        if not self.clipboard_manager:
            return
        
        # Clear existing items
        for i in reversed(range(self.clipboard_content_layout.count())):
            child = self.clipboard_content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add current clipboard history
        history = self.clipboard_manager.get_clipboard_history()
        
        if not history:
            no_history_label = QLabel("No clipboard history yet")
            no_history_label.setStyleSheet("""
                QLabel {
                    color: #7f8c8d; 
                    font-style: italic; 
                    font-size: 12px;
                    padding: 12px;
                    background: transparent;
                }
            """)
            self.clipboard_content_layout.addWidget(no_history_label)
        else:
            for i, item in enumerate(history):
                # Truncate long text for display based on config
                max_len = config.CLIPBOARD_DISPLAY_MAX_LENGTH
                display_text = item[:max_len] + "..." if len(item) > max_len else item
                
                clip_label = ClickableLabel(f"{i+1}. {display_text}")
                clip_label.clicked.connect(lambda text, full_text=item: self.copy_to_clipboard(full_text))
                self.clipboard_content_layout.addWidget(clip_label)
        
        # Add stretch to push items to top
        self.clipboard_content_layout.addStretch()
    
    def copy_to_clipboard(self, text: str):
        """
        Copy text to the clipboard.
        
        This method is called when a clickable label in the clipboard history
        is clicked. It uses the clipboard manager to copy the specified text
        to the system clipboard.
        
        Args:
            text (str): The text content to copy.
        """
        if self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(text)
    
    def add_note(self):
        """
        Add a new note to the database.
        
        This method is called when the user presses Enter in the note input field
        or clicks the "Add" button. It retrieves the title, content, and priority from the input fields,
        adds it to the database using the database manager, and refreshes the
        notes display.
        """
        title = self.title_input.text().strip()
        content = self.note_input.text().strip()
        priority = self.priority_input.currentIndex() + 1  # Convert from 0-based to 1-based
        
        # Must have at least content to create a note
        if content and self.database_manager:
            note_id = self.database_manager.add_note(content, title if title else None, priority)
            self.title_input.clear()
            self.note_input.clear()
            self.priority_input.setCurrentIndex(0)  # Reset to 1
            self.refresh_notes()
    
    def refresh_notes(self):
        """
        Refresh the display of notes in the dashboard.
        
        This method clears existing notes and repopulates the notes list
        with the latest notes from the database manager.
        """
        if not self.database_manager:
            return
        
        # Clear existing notes
        for i in reversed(range(self.notes_content_layout.count())):
            child = self.notes_content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add current notes
        notes = self.database_manager.get_all_notes()
        
        if not notes:
            no_notes_label = QLabel("No notes yet. Add your first note above!")
            no_notes_label.setStyleSheet("""
                QLabel {
                    color: #7f8c8d; 
                    font-style: italic; 
                    font-size: 12px;
                    padding: 12px;
                    background: transparent;
                }
            """)
            self.notes_content_layout.addWidget(no_notes_label)
        else:
            for note in notes:
                note_widget = EditableNoteWidget(note)
                note_widget.note_updated.connect(self.update_note)
                note_widget.note_deleted.connect(self.delete_note)
                note_widget.note_copied.connect(self.copy_to_clipboard)
                self.notes_content_layout.addWidget(note_widget)
        
        # Add stretch to push items to top
        self.notes_content_layout.addStretch()
        
        # Refresh notes window if it's open
        if self.notes_window and not self.notes_window.isHidden():
            self.notes_window.refresh_notes()
    
    def update_note(self, note_id: int, content: str, title: str, priority: int):
        """
        Update a note in the database.
        
        This method is called when a note widget emits a 'note_updated' signal.
        It uses the database manager to update the note content, title, and priority in the database.
        
        Args:
            note_id (int): The unique identifier of the note to update.
            content (str): The new content for the note.
            title (str): The new title for the note.
            priority (int): The new priority level for the note.
        """
        if self.database_manager:
            self.database_manager.update_note(note_id, content, title, priority)
    
    def delete_note(self, note_id: int):
        """
        Delete a note from the database.
        
        This method is called when a note widget emits a 'note_deleted' signal.
        It uses the database manager to delete the note from the database and
        refreshes the notes display.
        
        Args:
            note_id (int): The unique identifier of the note to delete.
        """
        if self.database_manager:
            self.database_manager.delete_note(note_id)
            self.refresh_notes()
    
    def toggle_visibility(self):
        """
        Toggle the visibility of the dashboard.
        
        This method handles the visibility hotkey trigger. It prints a message
        to the console and toggles the visibility of the dashboard.
        """
        print("Toggle visibility hotkey triggered!")
        if self.isVisible():
            print("Dashboard is visible, hiding it")
            self.hide()
        else:
            print("Dashboard is hidden, showing it")
            self.show()
            self.activateWindow()  # Bring to front
    
    def add_note_from_clipboard(self):
        """
        Add a note from the currently selected text.
        
        This method is called when the user triggers the "Add note from clipboard"
        hotkey. It saves the current clipboard content, simulates a Ctrl+C key
        press to copy the selected text, and then attempts to add it as a new
        note to the database. It also handles restoring the original clipboard
        content if the text was successfully added.
        """
        print("Add note from selected text hotkey triggered!")
        if self.clipboard_manager:
            # Import keyboard module for simulating key presses
            import keyboard
            import time
            
            # Save current clipboard content
            original_clipboard = self.clipboard_manager.get_current_clipboard()
            print(f"Original clipboard saved: {original_clipboard[:30] if original_clipboard else 'None'}...")
            
            # Simulate Ctrl+C to copy selected text
            keyboard.send('ctrl+c')
            time.sleep(0.1)  # Small delay to ensure copy completes
            
            # Get the newly copied text (selected text)
            selected_text = self.clipboard_manager.get_current_clipboard()
            
            # Check if we actually got new text and it's different from original
            if selected_text and selected_text != original_clipboard:
                print(f"Adding note from selected text: {selected_text[:30]}...")
                self.database_manager.add_note(selected_text)  # No title for clipboard notes
                self.refresh_notes()
                
                # Restore original clipboard content
                if original_clipboard:
                    time.sleep(0.1)  # Small delay
                    self.clipboard_manager.copy_to_clipboard(original_clipboard)
                    print("Original clipboard content restored")
            else:
                print("No text selected or same as clipboard - no note added")
                # If no text was selected, fall back to clipboard content
                if original_clipboard:
                    print(f"Falling back to clipboard content: {original_clipboard[:30]}...")
                    self.database_manager.add_note(original_clipboard)  # No title for clipboard notes
                    self.refresh_notes()
    
    def open_all_notes(self):
        """
        Open a new window to display all notes in a larger, more readable format.
        """
        # If window already exists and is visible, just bring it to front
        if self.notes_window and not self.notes_window.isHidden():
            self.notes_window.raise_()
            self.notes_window.activateWindow()
            return
        
        # Create new window or show existing one
        if not self.notes_window:
            self.notes_window = NotesWindow(self)
        
        self.notes_window.set_database_manager(self.database_manager)
        self.notes_window.show()
        self.notes_window.raise_()
        self.notes_window.activateWindow()
    
    def toggle_visibility_safe(self):
        """
        Thread-safe version of toggle_visibility.
        
        This method emits the toggle_visibility_signal to trigger the
        visibility toggle from a different thread.
        """
        self.toggle_visibility_signal.emit()
    
    def add_note_from_clipboard_safe(self):
        """
        Thread-safe version of add_note_from_clipboard.
        
        This method emits the add_note_from_clipboard_signal to trigger the
        clipboard hotkey from a different thread.
        """
        self.add_note_from_clipboard_signal.emit() 