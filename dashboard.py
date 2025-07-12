import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QListWidget, QListWidgetItem, 
                             QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                             QSplitter, QFrame, QScrollArea)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QSize, QThread, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QAction, QShortcut, QKeySequence
from typing import List, Dict, Optional, Callable
import threading
import config


class ClickableLabel(QLabel):
    """A clickable label that emits a signal when clicked."""
    clicked = pyqtSignal(str)
    
    def __init__(self, text: str, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.setWordWrap(True)
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
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.text())
        super().mousePressEvent(event)


class EditableNoteWidget(QWidget):
    """Widget for displaying and editing notes."""
    note_updated = pyqtSignal(int, str)
    note_deleted = pyqtSignal(int)
    note_copied = pyqtSignal(str)
    
    def __init__(self, note_data: Dict, parent=None):
        super().__init__(parent)
        self.note_data = note_data
        self.is_editing = False
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(4, 4, 4, 4)
        
        # Create main container
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
        
        container_layout = QVBoxLayout()
        container_layout.setSpacing(4)
        container_layout.setContentsMargins(6, 6, 6, 6)
        
        # Note content (display mode)
        self.display_label = QLabel(self.note_data['content'])
        self.display_label.setWordWrap(True)
        self.display_label.setStyleSheet("""
            QLabel {
                border: none; 
                background: transparent; 
                padding: 4px;
                color: #333333;
                font-size: 13px;
                line-height: 1.3;
            }
        """)
        
        # Note content (edit mode)
        self.edit_text = QTextEdit()
        self.edit_text.setPlainText(self.note_data['content'])
        self.edit_text.setMaximumHeight(60)  # Reduced from 80
        self.edit_text.setStyleSheet("""
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
        self.edit_text.hide()
        
        # Button container
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)
        
        # Edit button
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
        
        # Delete button
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
        
        # Save button (hidden initially)
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
        self.save_btn.hide()
        
        # Cancel button (hidden initially)
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
        self.cancel_btn.hide()
        
        # Copy button (positioned on the right side)
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
        
        # Add to container
        container_layout.addWidget(self.display_label)
        container_layout.addWidget(self.edit_text)
        container_layout.addLayout(button_layout)
        
        self.container.setLayout(container_layout)
        layout.addWidget(self.container)
        self.setLayout(layout)
    
    def toggle_edit_mode(self):
        """Toggle between display and edit mode."""
        self.is_editing = not self.is_editing
        
        if self.is_editing:
            self.display_label.hide()
            self.edit_text.show()
            self.edit_btn.hide()
            self.delete_btn.hide()
            self.save_btn.show()
            self.cancel_btn.show()
            self.edit_text.setFocus()
        else:
            self.display_label.show()
            self.edit_text.hide()
            self.edit_btn.show()
            self.delete_btn.show()
            self.save_btn.hide()
            self.cancel_btn.hide()
    
    def save_note(self):
        """Save the edited note."""
        new_content = self.edit_text.toPlainText().strip()
        if new_content:
            self.note_data['content'] = new_content
            self.display_label.setText(new_content)
            self.note_updated.emit(self.note_data['id'], new_content)
            self.toggle_edit_mode()
    
    def cancel_edit(self):
        """Cancel editing and revert changes."""
        self.edit_text.setPlainText(self.note_data['content'])
        self.toggle_edit_mode()
    
    def delete_note(self):
        """Delete the note after confirmation."""
        reply = QMessageBox.question(
            self, 
            "Delete Note", 
            "Are you sure you want to delete this note?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.note_deleted.emit(self.note_data['id'])
    
    def copy_note(self):
        """Copy the note content to clipboard."""
        self.note_copied.emit(self.note_data['content'])


class Dashboard(QMainWindow):
    """Main dashboard window for SnapPad."""
    
    # Define signals for thread-safe communication
    toggle_visibility_signal = pyqtSignal()
    add_note_from_clipboard_signal = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.clipboard_manager = None
        self.database_manager = None
        self.setup_ui()
        self.setup_window_properties()
        
        # Connect signals to their respective slots
        self.toggle_visibility_signal.connect(self.toggle_visibility)
        self.add_note_from_clipboard_signal.connect(self.add_note_from_clipboard)
        
        # Timer for refreshing clipboard history
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_clipboard_history)
        self.refresh_timer.start(config.REFRESH_INTERVAL)  # Refresh based on config
    
    def setup_ui(self):
        """Setup the user interface."""
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
        notes_layout.addWidget(notes_title)
        
        # Add note input
        add_note_layout = QHBoxLayout()
        add_note_layout.setSpacing(6)  # Reduced from 10
        
        self.note_input = QLineEdit()
        self.note_input.setPlaceholderText("Enter a new note...")
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
        
        add_note_layout.addWidget(self.note_input)
        add_note_layout.addWidget(add_note_btn)
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
        """Configure window properties."""
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
        """Set the clipboard and database managers."""
        self.clipboard_manager = clipboard_manager
        self.database_manager = database_manager
        
        # Load initial notes
        self.refresh_notes()
    
    def refresh_clipboard_history(self):
        """Refresh the clipboard history display."""
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
        """Copy text to clipboard."""
        if self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(text)
    
    def add_note(self):
        """Add a new note."""
        content = self.note_input.text().strip()
        if content and self.database_manager:
            note_id = self.database_manager.add_note(content)
            self.note_input.clear()
            self.refresh_notes()
    
    def refresh_notes(self):
        """Refresh the notes display."""
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
    
    def update_note(self, note_id: int, content: str):
        """Update a note in the database."""
        if self.database_manager:
            self.database_manager.update_note(note_id, content)
    
    def delete_note(self, note_id: int):
        """Delete a note from the database."""
        if self.database_manager:
            self.database_manager.delete_note(note_id)
            self.refresh_notes()
    
    def toggle_visibility(self):
        """Toggle the visibility of the dashboard."""
        print("Toggle visibility hotkey triggered!")
        if self.isVisible():
            print("Dashboard is visible, hiding it")
            self.hide()
        else:
            print("Dashboard is hidden, showing it")
            self.show()
            self.activateWindow()  # Bring to front
    
    def add_note_from_clipboard(self):
        """Add a note from the currently selected text."""
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
                self.database_manager.add_note(selected_text)
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
                    self.database_manager.add_note(original_clipboard)
                    self.refresh_notes()
    
    def toggle_visibility_safe(self):
        """Thread-safe version of toggle_visibility."""
        self.toggle_visibility_signal.emit()
    
    def add_note_from_clipboard_safe(self):
        """Thread-safe version of add_note_from_clipboard."""
        self.add_note_from_clipboard_signal.emit() 