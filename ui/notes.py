"""
Notes UI Components for SnapPad

This module contains UI components related to note management.
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                             QFrame, QComboBox, QDialog)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import Dict
from datetime import datetime


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
    
    def __init__(self, note_data: Dict, parent=None, is_compact=False):
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
            is_compact (bool): If True, show truncated content with "show all" button (for dashboard)
        """
        super().__init__(parent)
        
        # Store note data
        self.note_data = note_data
        
        # Track editing state
        self.is_editing = False
        
        # Store compact mode setting
        self.is_compact = is_compact
        self.is_content_expanded = False  # Track if content is expanded in compact mode
        
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
        # Main layout - compact margins for better space usage
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)  # Reduced from 4px
        
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
        
        # Container layout with compact spacing
        container_layout = QVBoxLayout()
        container_layout.setSpacing(3)  # Reduced from 4px
        container_layout.setContentsMargins(4, 4, 4, 4)  # Reduced from 6px
        
        # Header layout for title and priority
        header_layout = QHBoxLayout()
        header_layout.setSpacing(6)  # Reduced from 8px
        
        # Title display label (shown in display mode)
        self.title_display_label = QLabel(self.note_data['title'])
        self.title_display_label.setWordWrap(True)
        self.title_display_label.setStyleSheet("""
            QLabel {
                border: none; 
                background: transparent; 
                padding: 1px;
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
        edit_header_layout.setSpacing(6)  # Reduced from 8px
        
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
        self.content_display_label = QLabel()
        self.content_display_label.setWordWrap(True)
        self.content_display_label.setStyleSheet("""
            QLabel {
                border: none; 
                background: transparent; 
                padding: 2px;
                color: #333333;
                font-size: 13px;
                line-height: 1.3;
            }
        """)
        
        # Show all button for compact mode (hidden by default)
        self.show_all_btn = QPushButton("show all")
        self.show_all_btn.setMaximumWidth(60)
        self.show_all_btn.setMaximumHeight(20)
        self.show_all_btn.clicked.connect(self._toggle_content_display)
        self.show_all_btn.setStyleSheet("""
            QPushButton {
                background: #d1d0cf;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 2px 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #bcbab9;
            }
        """)
        self.show_all_btn.hide()  # Hidden by default
        
        # Set initial content based on compact mode
        self._update_content_display()
        
        # Note content text editor (shown in edit mode)
        self.content_edit_text = QTextEdit()
        self.content_edit_text.setPlainText(self.note_data['content'])
        self.content_edit_text.setMinimumHeight(80)  # Minimum height for visibility
        self.content_edit_text.setMaximumHeight(400)  # Allow expansion but prevent excessive height
        
        # Enable better text editing experience
        self.content_edit_text.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.content_edit_text.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.content_edit_text.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
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
                padding: 1px;
                color: #7f8c8d;
                font-size: 10px;
                font-style: italic;
            }
        """)
        
        # Button container layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(3)  # Reduced from 4px
        
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
        
        # Content section with show all button
        content_section_layout = QVBoxLayout()
        content_section_layout.setSpacing(2)
        content_section_layout.setContentsMargins(0, 0, 0, 0)
        content_section_layout.addWidget(self.content_display_label)
        
        # Show all button layout (right-aligned)
        show_all_layout = QHBoxLayout()
        show_all_layout.setContentsMargins(0, 0, 0, 0)
        show_all_layout.addStretch()
        show_all_layout.addWidget(self.show_all_btn)
        content_section_layout.addLayout(show_all_layout)
        
        # Add widgets to container layout
        container_layout.addWidget(self.display_header_widget)
        container_layout.addWidget(self.edit_header_widget)
        container_layout.addLayout(content_section_layout)
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
            self._update_content_display()  # Refresh content display after update
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
    
    def _update_content_display(self):
        """
        Update the content display based on compact mode and expansion state.
        """
        content = self.note_data['content']
        max_chars = 150  # Character limit for compact mode
        
        if self.is_compact and not self.is_content_expanded and len(content) > max_chars:
            # Show truncated content with "..."
            truncated_content = content[:max_chars].rstrip() + "..."
            self.content_display_label.setText(truncated_content)
            self.show_all_btn.show()
            self.show_all_btn.setText("show all")
        elif self.is_compact and self.is_content_expanded:
            # Show full content in compact mode
            self.content_display_label.setText(content)
            self.show_all_btn.show()
            self.show_all_btn.setText("show less")
        else:
            # Show full content (non-compact mode)
            self.content_display_label.setText(content)
            self.show_all_btn.hide()
    
    def _toggle_content_display(self):
        """
        Toggle between truncated and full content display in compact mode.
        """
        if self.is_compact:
            self.is_content_expanded = not self.is_content_expanded
            self._update_content_display()


class AddNoteDialog(QDialog):
    """
    Dialog window for adding new notes with title, content, and priority.
    
    This dialog provides a clean interface for creating new notes with all
    the necessary fields in a popup window.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the add note dialog.
        
        Args:
            parent: Parent widget (usually the main Dashboard)
        """
        super().__init__(parent)
        self.setup_ui()
        self.setup_window_properties()
    
    def setup_ui(self):
        """
        Set up the user interface for the add note dialog.
        """
        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        title_label = QLabel("Add New Note")
        title_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }
        """)
        layout.addWidget(title_label)
        
        # Title and priority input layout
        title_priority_layout = QHBoxLayout()
        title_priority_layout.setSpacing(10)
        
        # Title input
        self.title_input = QLineEdit()
        self.title_input.setPlaceholderText("Note title (optional)...")
        self.title_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                outline: none;
            }
        """)
        
        # Priority input
        self.priority_input = QComboBox()
        self.priority_input.addItems(["1", "2", "3"])
        self.priority_input.setCurrentIndex(0)  # Default to 1
        self.priority_input.setMaximumWidth(80)
        self.priority_input.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                font-size: 13px;
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
        layout.addLayout(title_priority_layout)
        
        # Content input
        content_label = QLabel("Content:")
        content_label.setStyleSheet("""
            QLabel {
                font-size: 13px;
                color: #2c3e50;
                margin-top: 5px;
            }
        """)
        layout.addWidget(content_label)
        
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Enter note content...")
        self.content_input.setMaximumHeight(120)
        self.content_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                padding: 10px;
                font-size: 14px;
                background-color: #ffffff;
                color: #2c3e50;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #4a90e2;
                outline: none;
            }
        """)
        layout.addWidget(self.content_input)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(35)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        
        # Add button
        add_btn = QPushButton("Add Note")
        add_btn.setMinimumHeight(35)
        add_btn.clicked.connect(self.accept_note)
        add_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        button_layout.addWidget(add_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_window_properties(self):
        """
        Configure window properties for the add note dialog.
        """
        self.setWindowTitle("Add New Note")
        self.setFixedSize(400, 300)
        self.setModal(True)
        
        # Center dialog on parent
        if self.parent():
            parent_rect = self.parent().geometry()
            x = parent_rect.x() + (parent_rect.width() - self.width()) // 2
            y = parent_rect.y() + (parent_rect.height() - self.height()) // 2
            self.move(x, y)
    
    def accept_note(self):
        """
        Accept the note if content is provided.
        """
        content = self.content_input.toPlainText().strip()
        if content:
            self.accept()
        else:
            QMessageBox.warning(self, "Missing Content", "Please enter note content before adding.")
    
    def get_note_data(self):
        """
        Get the note data from the dialog inputs.
        
        Returns:
            tuple: (title, content, priority)
        """
        title = self.title_input.text().strip()
        content = self.content_input.toPlainText().strip()
        priority = self.priority_input.currentIndex() + 1  # Convert from 0-based to 1-based
        return title, content, priority 