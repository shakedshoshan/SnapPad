"""
Window Classes for SnapPad

This module contains window classes for the SnapPad application.
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QComboBox, QFrame, QScrollArea, 
                             QTabWidget, QApplication, QMessageBox, QPushButton, QTextEdit)
from PyQt6.QtCore import Qt
from .notes import EditableNoteWidget


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
        
        # Main layout - reduced margins for better space usage
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(8, 8, 8, 8)  # Reduced from 20px to 8px
        main_layout.setSpacing(8)  # Reduced from 15px to 8px
        
        # Header with title and close button
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
            }
            QTabBar::tab {
                background: #f8f9fa;
                border: 1px solid #d1d5db;
                border-bottom: none;
                border-radius: 6px 6px 0 0;
                padding: 8px 16px;
                margin-right: 2px;
                font-size: 13px;
                font-weight: bold;
                color: #7f8c8d;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                color: #2c3e50;
                border-bottom: 2px solid #4a90e2;
            }
            QTabBar::tab:hover {
                background: #e9ecef;
                color: #2c3e50;
            }
        """)
        
        # Create All Notes tab
        self.all_notes_tab = QWidget()
        all_notes_layout = QVBoxLayout()
        all_notes_layout.setContentsMargins(0, 0, 0, 0)
        all_notes_layout.setSpacing(8)
        
        # Search and Sort section for All Notes tab
        all_notes_search_layout = QHBoxLayout()
        all_notes_search_layout.setSpacing(6)
        
        # Search bar for All Notes
        self.all_notes_search_input = QLineEdit()
        self.all_notes_search_input.setPlaceholderText("Search notes...")
        self.all_notes_search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        self.all_notes_search_input.textChanged.connect(self.refresh_all_notes)
        
        # Sort dropdown for All Notes
        self.all_notes_sort_combo = QComboBox()
        self.all_notes_sort_combo.addItems([
            "Updated (newest)",
            "Updated (oldest)", 
            "Created (newest)",
            "Created (oldest)",
            "Priority (high)",
            "Priority (low)",
            "Title (A-Z)",
            "Title (Z-A)"
        ])
        self.all_notes_sort_combo.setCurrentIndex(0)
        self.all_notes_sort_combo.setMaximumWidth(150)
        self.all_notes_sort_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
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
        self.all_notes_sort_combo.currentTextChanged.connect(self.refresh_all_notes)
        
        all_notes_search_layout.addWidget(self.all_notes_search_input)
        all_notes_search_layout.addWidget(self.all_notes_sort_combo)
        
        # Notes container for All Notes tab
        self.all_notes_container = QFrame()
        self.all_notes_container.setFrameStyle(QFrame.Shape.Box)
        self.all_notes_container.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
                padding: 4px;
            }
        """)
        
        all_notes_container_layout = QVBoxLayout()
        all_notes_container_layout.setSpacing(6)
        all_notes_container_layout.setContentsMargins(4, 4, 4, 4)
        
        # Notes scroll area for All Notes tab
        self.all_notes_scroll = QScrollArea()
        self.all_notes_scroll.setWidgetResizable(True)
        self.all_notes_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.all_notes_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.all_notes_scroll.setStyleSheet("""
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
        
        self.all_notes_content = QWidget()
        self.all_notes_content_layout = QVBoxLayout()
        self.all_notes_content_layout.setSpacing(6)
        self.all_notes_content_layout.setContentsMargins(4, 4, 4, 4)
        self.all_notes_content.setLayout(self.all_notes_content_layout)
        self.all_notes_scroll.setWidget(self.all_notes_content)
        
        all_notes_container_layout.addWidget(self.all_notes_scroll)
        self.all_notes_container.setLayout(all_notes_container_layout)
        
        all_notes_layout.addLayout(all_notes_search_layout)
        all_notes_layout.addWidget(self.all_notes_container)
        self.all_notes_tab.setLayout(all_notes_layout)
        
        # Create Enhanced Prompts tab
        self.enhanced_prompts_tab = QWidget()
        enhanced_prompts_layout = QVBoxLayout()
        enhanced_prompts_layout.setContentsMargins(0, 0, 0, 0)
        enhanced_prompts_layout.setSpacing(8)
        
        # Create Smart Response Generation tab
        self.smart_response_tab = QWidget()
        smart_response_layout = QVBoxLayout()
        smart_response_layout.setContentsMargins(0, 0, 0, 0)
        smart_response_layout.setSpacing(8)
        
        # Prompt Enhancement Section
        prompt_frame = QFrame()
        prompt_frame.setFrameStyle(QFrame.Shape.Box)
        prompt_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
                padding: 8px;
            }
        """)
        prompt_layout = QVBoxLayout()
        prompt_layout.setSpacing(8)
        prompt_layout.setContentsMargins(8, 8, 8, 8)
        
        # Prompt header
        prompt_header_layout = QHBoxLayout()
        prompt_header_layout.setSpacing(10)
        
        prompt_title = QLabel("🤖 AI Prompt Enhancement")
        prompt_title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 14px;
                color: #2c3e50;
                margin-bottom: 2px;
                background: transparent;
            }
        """)
        
        prompt_header_layout.addWidget(prompt_title)
        prompt_header_layout.addStretch()
        
        prompt_layout.addLayout(prompt_header_layout)
        
        # Prompt input area
        prompt_input_label = QLabel("Paste your prompt here:")
        prompt_input_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        prompt_layout.addWidget(prompt_input_label)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(100)
        self.prompt_input.setPlaceholderText("Paste your prompt here and click 'Enhance' to get an improved version...")
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QTextEdit:focus {
                border-color: #4a90e2;
            }
        """)
        prompt_layout.addWidget(self.prompt_input)
        
        # Loading spinner
        from .components import LoadingSpinner
        self.loading_spinner = LoadingSpinner()
        prompt_layout.addWidget(self.loading_spinner)
        
        # Enhance button
        self.enhance_btn = QPushButton("Enhance Prompt")
        self.enhance_btn.clicked.connect(self.enhance_prompt)
        self.enhance_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d35400;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        prompt_layout.addWidget(self.enhance_btn)
        
        # Enhanced prompt display
        enhanced_label = QLabel("Enhanced prompt:")
        enhanced_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        prompt_layout.addWidget(enhanced_label)
        
        self.enhanced_prompt_display = QTextEdit()
        self.enhanced_prompt_display.setMaximumHeight(150)
        self.enhanced_prompt_display.setReadOnly(True)
        self.enhanced_prompt_display.setPlaceholderText("Enhanced prompt will appear here...")
        self.enhanced_prompt_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)
        prompt_layout.addWidget(self.enhanced_prompt_display)
        
        # Copy enhanced prompt button
        self.copy_enhanced_btn = QPushButton("Copy Enhanced")
        self.copy_enhanced_btn.clicked.connect(self.copy_enhanced_prompt)
        self.copy_enhanced_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        prompt_layout.addWidget(self.copy_enhanced_btn)
        
        # Status label for feedback
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 11px;
                font-style: italic;
                background: transparent;
                padding: 2px;
            }
        """)
        prompt_layout.addWidget(self.status_label)
        
        prompt_frame.setLayout(prompt_layout)
        enhanced_prompts_layout.addWidget(prompt_frame)
        self.enhanced_prompts_tab.setLayout(enhanced_prompts_layout)
        
        # Smart Response Generation Section
        smart_response_frame = QFrame()
        smart_response_frame.setFrameStyle(QFrame.Shape.Box)
        smart_response_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
                padding: 8px;
            }
        """)
        smart_response_layout_inner = QVBoxLayout()
        smart_response_layout_inner.setSpacing(8)
        smart_response_layout_inner.setContentsMargins(8, 8, 8, 8)
        
        # Smart response header
        smart_response_header_layout = QHBoxLayout()
        smart_response_header_layout.setSpacing(10)
        
        smart_response_title = QLabel("🧠 AI Smart Response Generation")
        smart_response_title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 14px;
                color: #2c3e50;
                margin-bottom: 2px;
                background: transparent;
            }
        """)
        
        smart_response_header_layout.addWidget(smart_response_title)
        smart_response_header_layout.addStretch()
        
        smart_response_layout_inner.addLayout(smart_response_header_layout)
        

        
        # Smart response input area
        smart_response_input_label = QLabel("Enter your question, code, or prompt:")
        smart_response_input_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        smart_response_layout_inner.addWidget(smart_response_input_label)
        
        self.smart_response_input = QTextEdit()
        self.smart_response_input.setMaximumHeight(120)
        self.smart_response_input.setPlaceholderText("Ask a question, paste code for review, or enter any prompt for AI response...")
        self.smart_response_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QTextEdit:focus {
                border-color: #4a90e2;
            }
        """)
        smart_response_layout_inner.addWidget(self.smart_response_input)
        
        # Smart response loading spinner
        from .components import LoadingSpinner
        self.smart_response_loading_spinner = LoadingSpinner()
        smart_response_layout_inner.addWidget(self.smart_response_loading_spinner)
        
        # Generate response button
        self.smart_response_generate_btn = QPushButton("Generate Response")
        self.smart_response_generate_btn.clicked.connect(self.generate_smart_response)
        self.smart_response_generate_btn.setStyleSheet("""
            QPushButton {
                background: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #8e44ad;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        smart_response_layout_inner.addWidget(self.smart_response_generate_btn)
        
        # Generated response display
        generated_response_label = QLabel("AI Response:")
        generated_response_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        smart_response_layout_inner.addWidget(generated_response_label)
        
        self.smart_response_display = QTextEdit()
        self.smart_response_display.setMaximumHeight(200)
        self.smart_response_display.setReadOnly(True)
        self.smart_response_display.setPlaceholderText("AI response will appear here...")
        self.smart_response_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 13px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)
        smart_response_layout_inner.addWidget(self.smart_response_display)
        
        # Copy generated response button
        self.smart_response_copy_btn = QPushButton("Copy Response")
        self.smart_response_copy_btn.clicked.connect(self.copy_smart_response)
        self.smart_response_copy_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        smart_response_layout_inner.addWidget(self.smart_response_copy_btn)
        
        # Status label for feedback
        self.smart_response_status_label = QLabel("")
        self.smart_response_status_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 11px;
                font-style: italic;
                background: transparent;
                padding: 2px;
            }
        """)
        smart_response_layout_inner.addWidget(self.smart_response_status_label)
        
        smart_response_frame.setLayout(smart_response_layout_inner)
        smart_response_layout.addWidget(smart_response_frame)
        self.smart_response_tab.setLayout(smart_response_layout)
        
        # Add tabs to tab widget
        self.tab_widget.addTab(self.all_notes_tab, "📝 All Notes")
        self.tab_widget.addTab(self.enhanced_prompts_tab, "🤖 Enhanced Prompts")
        self.tab_widget.addTab(self.smart_response_tab, "🧠 Smart Response")
        
        # Add to main layout
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.tab_widget)
        
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
        self.refresh_all_notes()
    
    def _filter_and_sort_notes(self, notes, search_input=None, sort_combo=None):
        """
        Filter and sort notes based on search and sort criteria.
        
        Args:
            notes: List of note dictionaries
            search_input: The search input widget (optional)
            sort_combo: The sort combo box widget (optional)
            
        Returns:
            List of filtered and sorted notes
        """
        # Filter by search term
        search_term = ""
        if search_input and hasattr(search_input, 'text'):
            search_term = search_input.text().strip().lower()
        
        if search_term:
            notes = [note for note in notes 
                    if search_term in note['title'].lower() or 
                       search_term in note['content'].lower()]
        
        # Sort based on selected criteria
        sort_option = "Updated (newest)"  # Default
        if sort_combo and hasattr(sort_combo, 'currentText'):
            sort_option = sort_combo.currentText()
        
        if sort_option == "Updated (newest)":
            notes.sort(key=lambda x: x['updated_at'], reverse=True)
        elif sort_option == "Updated (oldest)":
            notes.sort(key=lambda x: x['updated_at'], reverse=False)
        elif sort_option == "Created (newest)":
            notes.sort(key=lambda x: x['created_at'], reverse=True)
        elif sort_option == "Created (oldest)":
            notes.sort(key=lambda x: x['created_at'], reverse=False)
        elif sort_option == "Priority (high)":
            notes.sort(key=lambda x: x['priority'], reverse=True)
        elif sort_option == "Priority (low)":
            notes.sort(key=lambda x: x['priority'], reverse=False)
        elif sort_option == "Title (A-Z)":
            notes.sort(key=lambda x: x['title'].lower(), reverse=False)
        elif sort_option == "Title (Z-A)":
            notes.sort(key=lambda x: x['title'].lower(), reverse=True)
        
        return notes
    
    def refresh_all_notes(self):
        """
        Refresh the display of all notes in the All Notes tab.
        """
        if not self.database_manager:
            return
        
        # Clear existing notes
        for i in reversed(range(self.all_notes_content_layout.count())):
            child = self.all_notes_content_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get, filter, and sort notes
        all_notes = self.database_manager.get_all_notes()
        notes = self._filter_and_sort_notes(all_notes, self.all_notes_search_input, self.all_notes_sort_combo)
        
        if not notes:
            # Check if we have notes but they're filtered out
            if all_notes and self.all_notes_search_input.text().strip():
                no_notes_label = QLabel("No notes match your search criteria.")
            else:
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
            self.all_notes_content_layout.addWidget(no_notes_label)
        else:
            for note in notes:
                note_widget = EditableNoteWidget(note)
                note_widget.note_updated.connect(self.update_note)
                note_widget.note_deleted.connect(self.delete_note)
                note_widget.note_copied.connect(self.copy_to_clipboard)
                self.all_notes_content_layout.addWidget(note_widget)
        
        # Add stretch to push items to top
        self.all_notes_content_layout.addStretch()
    
    def enhance_prompt(self):
        """
        Enhance the prompt in the input field using OpenAI API.
        """
        if not hasattr(self, 'openai_manager') or not self.openai_manager:
            QMessageBox.warning(self, "OpenAI Not Available", 
                              "OpenAI features are not enabled or configured.")
            return
        
        # Get the prompt from input
        original_prompt = self.prompt_input.toPlainText().strip()
        
        if not original_prompt:
            QMessageBox.warning(self, "No Prompt", 
                              "Please enter a prompt to enhance.")
            return
        
        # Show loading spinner and disable button
        self.loading_spinner.start_animation()
        self.enhance_btn.setEnabled(False)
        self.enhance_btn.setText("Enhancing...")
        self.copy_enhanced_btn.setEnabled(False)
        
        # Create and start worker thread
        from .workers import OpenAIWorker
        self.openai_worker = OpenAIWorker(self.openai_manager, original_prompt)
        self.openai_worker.enhancement_complete.connect(self.on_enhancement_complete)
        self.openai_worker.enhancement_failed.connect(self.on_enhancement_failed)
        self.openai_worker.finished.connect(self.on_worker_finished)
        self.openai_worker.start()
    
    def on_enhancement_complete(self, enhanced_prompt):
        """
        Handle successful prompt enhancement.
        
        Args:
            enhanced_prompt (str): The enhanced prompt text
        """
        # Display the enhanced prompt
        self.enhanced_prompt_display.setPlainText(enhanced_prompt)
        self.copy_enhanced_btn.setEnabled(True)
        
        # Automatically copy the enhanced prompt to clipboard
        if hasattr(self, 'clipboard_manager') and self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(enhanced_prompt)
            print(f"Enhanced prompt automatically copied to clipboard: {enhanced_prompt[:50]}...")
        
        # Replace the original prompt with the enhanced version
        self.prompt_input.setPlainText(enhanced_prompt)
        
        # Automatically paste the enhanced text to replace selected text
        import keyboard
        import time
        time.sleep(0.2)  # Slightly longer delay to ensure clipboard is ready and user sees the process
        keyboard.send('ctrl+v')
        print("Enhanced prompt automatically pasted to replace selected text")
        
        # Show success status message
        self.status_label.setText("✓ Enhanced prompt pasted and input updated")
        
        # Clear status message after 3 seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.status_label.setText(""))
        
        print(f"Enhancement completed successfully: {enhanced_prompt[:50]}...")
        print("Original prompt replaced with enhanced version")
    
    def on_enhancement_failed(self, error_message):
        """
        Handle failed prompt enhancement.
        
        Args:
            error_message (str): The error message
        """
        QMessageBox.warning(self, "Enhancement Failed", 
                          f"Failed to enhance prompt: {error_message}")
        print(f"Enhancement failed: {error_message}")
    
    def on_worker_finished(self):
        """
        Handle worker thread completion.
        """
        self.loading_spinner.stop_animation()
        self.enhance_btn.setEnabled(True)
        self.enhance_btn.setText("Enhance Prompt")
        print("OpenAI worker finished")
    
    def copy_enhanced_prompt(self):
        """
        Copy the enhanced prompt to the clipboard.
        """
        enhanced_text = self.enhanced_prompt_display.toPlainText()
        if enhanced_text and hasattr(self, 'clipboard_manager') and self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(enhanced_text)
            print("Enhanced prompt copied to clipboard")
            
            # Show feedback for manual copy
            self.status_label.setText("✓ Enhanced prompt copied to clipboard")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.status_label.setText(""))
    
    def set_openai_manager(self, openai_manager):
        """
        Set the OpenAI manager for the notes window.
        
        Args:
            openai_manager: The OpenAI manager instance
        """
        self.openai_manager = openai_manager
    
    def set_clipboard_manager(self, clipboard_manager):
        """
        Set the clipboard manager for the notes window.
        
        Args:
            clipboard_manager: The clipboard manager instance
        """
        self.clipboard_manager = clipboard_manager
    
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
            self.refresh_all_notes()
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
            self.refresh_all_notes()
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
    
    # =============================================================================
    # SMART RESPONSE GENERATION METHODS
    # =============================================================================
    
    def generate_smart_response(self):
        """
        Generate a smart response to the user input using OpenAI API.
        """
        if not hasattr(self, 'openai_manager') or not self.openai_manager:
            QMessageBox.warning(self, "OpenAI Not Available", 
                              "OpenAI features are not enabled or configured.")
            return
        
        # Get the user input
        user_input = self.smart_response_input.toPlainText().strip()
        
        if not user_input:
            QMessageBox.warning(self, "No Input", 
                              "Please enter some text to generate a response for.")
            return
        
        # Show loading spinner and disable button
        self.smart_response_loading_spinner.start_animation()
        self.smart_response_generate_btn.setEnabled(False)
        self.smart_response_generate_btn.setText("Generating...")
        self.smart_response_copy_btn.setEnabled(False)
        
        # Create and start worker thread
        from .workers import SmartResponseWorker
        self.smart_response_worker = SmartResponseWorker(self.openai_manager, user_input, "general")
        self.smart_response_worker.response_complete.connect(self.on_smart_response_complete)
        self.smart_response_worker.response_failed.connect(self.on_smart_response_failed)
        self.smart_response_worker.finished.connect(self.on_smart_response_worker_finished)
        self.smart_response_worker.start()
    
    def on_smart_response_complete(self, generated_response):
        """
        Handle successful smart response generation.
        
        Args:
            generated_response (str): The generated response text
        """
        # Display the generated response
        self.smart_response_display.setPlainText(generated_response)
        self.smart_response_copy_btn.setEnabled(True)
        
        # Automatically copy the generated response to clipboard
        if hasattr(self, 'clipboard_manager') and self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(generated_response)
            print(f"Generated response automatically copied to clipboard: {generated_response[:50]}...")
        
        # Replace the original input with the generated response
        self.smart_response_input.setPlainText(generated_response)
        
        # Automatically paste the generated text to replace selected text
        import keyboard
        import time
        time.sleep(0.1)  # Small delay to ensure clipboard is ready
        keyboard.send('ctrl+v')
        print("Generated response automatically pasted to replace selected text")
        
        # Show success status message
        self.smart_response_status_label.setText("✓ Generated response pasted and input updated")
        
        # Clear status message after 3 seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.smart_response_status_label.setText(""))
        
        print(f"Smart response generation completed successfully: {generated_response[:50]}...")
        print("Original input replaced with generated response")
    
    def on_smart_response_failed(self, error_message):
        """
        Handle failed smart response generation.
        
        Args:
            error_message (str): The error message
        """
        QMessageBox.warning(self, "Response Generation Failed", 
                          f"Failed to generate response: {error_message}")
        print(f"Response generation failed: {error_message}")
    
    def on_smart_response_worker_finished(self):
        """
        Handle smart response worker thread completion.
        """
        self.smart_response_loading_spinner.stop_animation()
        self.smart_response_generate_btn.setEnabled(True)
        self.smart_response_generate_btn.setText("Generate Response")
        print("Smart response worker finished")
    
    def copy_smart_response(self):
        """
        Copy the generated response to the clipboard.
        """
        response_text = self.smart_response_display.toPlainText()
        if response_text and hasattr(self, 'clipboard_manager') and self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(response_text)
            print("Generated response copied to clipboard")
            
            # Show feedback for manual copy
            self.smart_response_status_label.setText("✓ Generated response copied to clipboard")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.smart_response_status_label.setText("")) 