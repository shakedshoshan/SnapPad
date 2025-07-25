"""
Main Dashboard for SnapPad

This module contains the main dashboard window that orchestrates all UI components.
"""

import sys
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QLineEdit, QPushButton, QTextEdit, QMessageBox, 
                             QSplitter, QFrame, QScrollArea, QComboBox,
                             QApplication, QProgressBar, QDialog)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, pyqtSlot
from PyQt6.QtGui import QFont, QIcon, QAction, QShortcut, QKeySequence
from typing import List, Dict, Optional, Callable
import threading
from datetime import datetime
import config

# Import UI components
from .components import LoadingSpinner, ClickableLabel
from .workers import OpenAIWorker, SmartResponseWorker
from .notes import EditableNoteWidget, AddNoteDialog
from .windows import NotesWindow
from .settings import SettingsWindow


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
    enhance_prompt_from_clipboard_signal = pyqtSignal()
    generate_smart_response_from_clipboard_signal = pyqtSignal()
    
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
        self.openai_manager = None
        
        # Initialize notes window reference
        self.notes_window = None
        
        # Initialize settings window reference
        self.settings_window = None
        
        # Initialize worker thread
        self.openai_worker = None
        
        # Load settings and apply them (this will set up the UI)
        self.load_and_apply_settings()
        
        # Apply initial size adjustment if settings were loaded
        try:
            from .settings import SettingsWindow
            temp_settings = SettingsWindow()
            settings = temp_settings.get_settings()
            temp_settings.close()
            self.adjust_dashboard_size(settings)
        except Exception as e:
            print(f"Error applying initial size adjustment: {e}")
        
        # Configure window properties
        self.setup_window_properties()
        
        # Connect signals to their respective slots
        self.toggle_visibility_signal.connect(self.toggle_visibility)
        self.add_note_from_clipboard_signal.connect(self.add_note_from_clipboard)
        self.enhance_prompt_from_clipboard_signal.connect(self.enhance_prompt_from_clipboard)
        self.generate_smart_response_from_clipboard_signal.connect(self.generate_smart_response_from_clipboard)
        
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
        
        # Header layout
        header_layout = QHBoxLayout()
        
        # Settings button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setMaximumWidth(30)
        self.settings_btn.setMaximumHeight(24)
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        
        header_layout.addWidget(self.settings_btn)
        header_layout.addStretch()
        
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
        
        # Add Note button
        self.add_note_btn = QPushButton("Add")
        self.add_note_btn.setMaximumWidth(50)
        self.add_note_btn.setMaximumHeight(24)
        self.add_note_btn.clicked.connect(self.show_add_note_dialog)
        self.add_note_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
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
        notes_header_layout.addWidget(self.add_note_btn)
        notes_header_layout.addWidget(self.open_notes_btn)
        
        notes_layout.addLayout(notes_header_layout)
        
        # Search and Sort section
        search_sort_layout = QHBoxLayout()
        search_sort_layout.setSpacing(6)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        self.search_input.textChanged.connect(self.refresh_notes)
        
        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Updated (newest)",
            "Updated (oldest)", 
            "Created (newest)",
            "Created (oldest)",
            "Priority (high)",
            "Priority (low)",
            "Title (A-Z)",
            "Title (Z-A)"
        ])
        self.sort_combo.setCurrentIndex(0)  # Default to "Updated (newest)"
        self.sort_combo.setMaximumWidth(120)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
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
        self.sort_combo.currentTextChanged.connect(self.refresh_notes)
        
        search_sort_layout.addWidget(self.search_input)
        search_sort_layout.addWidget(self.sort_combo)
        notes_layout.addLayout(search_sort_layout)
        
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
        
        # Prompt Enhancement Section (only if OpenAI is enabled)
        if config.OPENAI_ENABLED:
            prompt_frame = QFrame()
            prompt_frame.setFrameStyle(QFrame.Shape.Box)
            prompt_frame.setStyleSheet("""
                QFrame {
                    border: 1px solid #d1d5db;
                    border-radius: 6px;
                    background: #ffffff;
                    padding: 4px;
                }
            """)
            prompt_layout = QVBoxLayout()
            prompt_layout.setSpacing(6)
            prompt_layout.setContentsMargins(6, 6, 6, 6)
            
            # Prompt header
            prompt_header_layout = QHBoxLayout()
            prompt_header_layout.setSpacing(10)
            
            prompt_title = QLabel("🤖 AI Prompt Enhancement")
            prompt_title.setStyleSheet("""
                QLabel {
                    font-weight: bold; 
                    font-size: 13px;
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
                    font-size: 11px;
                    color: #7f8c8d;
                    background: transparent;
                }
            """)
            prompt_layout.addWidget(prompt_input_label)
            
            self.prompt_input = QTextEdit()
            self.prompt_input.setMaximumHeight(80)
            self.prompt_input.setPlaceholderText("Paste your prompt here and click 'Enhance' to get an improved version...")
            self.prompt_input.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 12px;
                    background-color: #ffffff;
                    color: #2c3e50;
                }
                QTextEdit:focus {
                    border-color: #4a90e2;
                }
            """)
            prompt_layout.addWidget(self.prompt_input)
            
            # Loading spinner
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
                    padding: 8px;
                    font-size: 12px;
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
                    font-size: 11px;
                    color: #7f8c8d;
                    background: transparent;
                }
            """)
            prompt_layout.addWidget(enhanced_label)
            
            self.enhanced_prompt_display = QTextEdit()
            self.enhanced_prompt_display.setMaximumHeight(120)
            self.enhanced_prompt_display.setReadOnly(True)
            self.enhanced_prompt_display.setPlaceholderText("Enhanced prompt will appear here...")
            self.enhanced_prompt_display.setStyleSheet("""
                QTextEdit {
                    border: 1px solid #d1d5db;
                    border-radius: 4px;
                    padding: 6px;
                    font-size: 12px;
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
                    padding: 6px;
                    font-size: 11px;
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
                    font-size: 10px;
                    font-style: italic;
                    background: transparent;
                    padding: 2px;
                }
            """)
            prompt_layout.addWidget(self.status_label)
            
            prompt_frame.setLayout(prompt_layout)
            
            # Smart Response Section (only if OpenAI is enabled)
            if config.SMART_RESPONSE_ENABLED:
                smart_response_frame = QFrame()
                smart_response_frame.setFrameStyle(QFrame.Shape.Box)
                smart_response_frame.setStyleSheet("""
                    QFrame {
                        border: 1px solid #d1d5db;
                        border-radius: 6px;
                        background: #ffffff;
                        padding: 4px;
                    }
                """)
                smart_response_layout = QVBoxLayout()
                smart_response_layout.setSpacing(6)
                smart_response_layout.setContentsMargins(6, 6, 6, 6)
                
                # Smart response header
                smart_response_header_layout = QHBoxLayout()
                smart_response_header_layout.setSpacing(10)
                
                smart_response_title = QLabel("🧠 AI Smart Response")
                smart_response_title.setStyleSheet("""
                    QLabel {
                        font-weight: bold; 
                        font-size: 13px;
                        color: #2c3e50;
                        margin-bottom: 2px;
                        background: transparent;
                    }
                """)
                
                smart_response_header_layout.addWidget(smart_response_title)
                smart_response_header_layout.addStretch()
                
                smart_response_layout.addLayout(smart_response_header_layout)
                

                
                # Smart response input area
                smart_response_input_label = QLabel("Enter your question, code, or prompt:")
                smart_response_input_label.setStyleSheet("""
                    QLabel {
                        font-size: 11px;
                        color: #7f8c8d;
                        background: transparent;
                    }
                """)
                smart_response_layout.addWidget(smart_response_input_label)
                
                self.smart_response_input = QTextEdit()
                self.smart_response_input.setMaximumHeight(80)
                self.smart_response_input.setPlaceholderText("Ask a question, paste code for review, or enter any prompt for AI response...")
                self.smart_response_input.setStyleSheet("""
                    QTextEdit {
                        border: 1px solid #d1d5db;
                        border-radius: 4px;
                        padding: 6px;
                        font-size: 12px;
                        background-color: #ffffff;
                        color: #2c3e50;
                    }
                    QTextEdit:focus {
                        border-color: #4a90e2;
                    }
                """)
                smart_response_layout.addWidget(self.smart_response_input)
                
                # Smart response loading spinner
                self.smart_response_loading_spinner = LoadingSpinner()
                smart_response_layout.addWidget(self.smart_response_loading_spinner)
                
                # Generate response button
                self.generate_response_btn = QPushButton("Generate Response")
                self.generate_response_btn.clicked.connect(self.generate_smart_response)
                self.generate_response_btn.setStyleSheet("""
                    QPushButton {
                        background: #9b59b6;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 8px;
                        font-size: 12px;
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
                smart_response_layout.addWidget(self.generate_response_btn)
                
                # Generated response display
                generated_response_label = QLabel("AI Response:")
                generated_response_label.setStyleSheet("""
                    QLabel {
                        font-size: 11px;
                        color: #7f8c8d;
                        background: transparent;
                    }
                """)
                smart_response_layout.addWidget(generated_response_label)
                
                self.generated_response_display = QTextEdit()
                self.generated_response_display.setMaximumHeight(120)
                self.generated_response_display.setReadOnly(True)
                self.generated_response_display.setPlaceholderText("AI response will appear here...")
                self.generated_response_display.setStyleSheet("""
                    QTextEdit {
                        border: 1px solid #d1d5db;
                        border-radius: 4px;
                        padding: 6px;
                        font-size: 12px;
                        background-color: #f8f9fa;
                        color: #2c3e50;
                    }
                """)
                smart_response_layout.addWidget(self.generated_response_display)
                
                # Copy generated response button
                self.copy_response_btn = QPushButton("Copy Response")
                self.copy_response_btn.clicked.connect(self.copy_generated_response)
                self.copy_response_btn.setStyleSheet("""
                    QPushButton {
                        background: #27ae60;
                        color: white;
                        border: none;
                        border-radius: 4px;
                        padding: 6px;
                        font-size: 11px;
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
                smart_response_layout.addWidget(self.copy_response_btn)
                
                # Status label for feedback
                self.smart_response_status_label = QLabel("")
                self.smart_response_status_label.setStyleSheet("""
                    QLabel {
                        color: #27ae60;
                        font-size: 10px;
                        font-style: italic;
                        background: transparent;
                        padding: 2px;
                    }
                """)
                smart_response_layout.addWidget(self.smart_response_status_label)
                
                smart_response_frame.setLayout(smart_response_layout)
                
                # Add frames to splitter
                splitter.addWidget(clipboard_frame)
                splitter.addWidget(notes_frame)
                splitter.addWidget(prompt_frame)
                splitter.addWidget(smart_response_frame)
                splitter.setSizes([200, 200, 200, 200])  # Initial sizes
            else:
                # Add frames to splitter (without smart response)
                splitter.addWidget(clipboard_frame)
                splitter.addWidget(notes_frame)
                splitter.addWidget(prompt_frame)
                splitter.setSizes([200, 250, 200])  # Initial sizes
        else:
            # Add frames to splitter (without prompt enhancement)
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
        
        # Set minimum size instead of fixed size to allow dynamic resizing
        self.setMinimumSize(config.DASHBOARD_WIDTH, config.DASHBOARD_HEIGHT)
        self.resize(config.DASHBOARD_WIDTH, config.DASHBOARD_HEIGHT)
        
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
    
    def set_managers(self, clipboard_manager, database_manager, openai_manager=None):
        """
        Set the clipboard and database managers for the dashboard.
        
        This method assigns the provided managers to the dashboard's attributes
        and triggers a refresh of the notes display.
        
        Args:
            clipboard_manager: The manager responsible for clipboard operations.
            database_manager: The manager responsible for managing notes.
            openai_manager: The manager responsible for OpenAI API operations (optional).
        """
        self.clipboard_manager = clipboard_manager
        self.database_manager = database_manager
        self.openai_manager = openai_manager
        
        # Load initial notes and clipboard history with a small delay to ensure UI is ready
        QTimer.singleShot(100, self.refresh_notes)
        QTimer.singleShot(100, self.refresh_clipboard_history)
    
    def refresh_clipboard_history(self):
        """
        Refresh the display of clipboard history items.
        
        This method clears existing items and repopulates the clipboard history
        display with the latest history from the clipboard manager.
        """
        try:
            if not self.clipboard_manager:
                return
            
            # Check if UI elements still exist (they might be deleted during rebuild)
            if not hasattr(self, 'clipboard_content_layout') or self.clipboard_content_layout is None:
                return
            
            # Additional safety check
            try:
                self.clipboard_content_layout.count()
            except Exception as e:
                return
            
            # Clear existing items
            for i in reversed(range(self.clipboard_content_layout.count())):
                child = self.clipboard_content_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
        except Exception as e:
            print(f"Error in refresh_clipboard_history: {e}")
            return
        
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
                # Fix: Use a default parameter to capture the current value of item
                clip_label.clicked.connect(lambda checked, full_text=item: self.copy_to_clipboard(full_text))
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
    
    def show_add_note_dialog(self):
        """
        Show the add note dialog and handle the result.
        """
        dialog = AddNoteDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            title, content, priority = dialog.get_note_data()
            self.add_note(title, content, priority)
    
    def add_note(self, title=None, content=None, priority=1):
        """
        Add a new note to the database.
        
        This method adds a note to the database using the database manager and refreshes
        the notes display.
        
        Args:
            title (str, optional): The title of the note
            content (str): The content of the note  
            priority (int): The priority level (1-3)
        """
        # Must have at least content to create a note
        if content and self.database_manager:
            note_id = self.database_manager.add_note(content, title if title else None, priority)
            self.refresh_notes()
    
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
    
    def refresh_notes(self):
        """
        Refresh the display of notes in the dashboard.
        
        This method clears existing notes and repopulates the notes list
        with the latest notes from the database manager, applying search and sort filters.
        """
        try:
            if not self.database_manager:
                return
            
            # Check if UI elements still exist (they might be deleted during rebuild)
            if not hasattr(self, 'notes_content_layout') or self.notes_content_layout is None:
                return
            
            # Additional safety check
            try:
                self.notes_content_layout.count()
            except Exception as e:
                return
            
            # Clear existing notes
            for i in reversed(range(self.notes_content_layout.count())):
                child = self.notes_content_layout.itemAt(i).widget()
                if child:
                    child.setParent(None)
        except Exception as e:
            print(f"Error in refresh_notes: {e}")
            return
        
        # Get, filter, and sort notes
        all_notes = self.database_manager.get_all_notes()
        notes = self._filter_and_sort_notes(all_notes, self.search_input, self.sort_combo)
        
        if not notes:
            # Check if we have notes but they're filtered out
            if all_notes and hasattr(self, 'search_input') and self.search_input.text().strip():
                no_notes_label = QLabel("No notes match your search criteria.")
            else:
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
                note_widget = EditableNoteWidget(note, is_compact=True)  # Compact mode for dashboard
                note_widget.note_updated.connect(self.update_note)
                note_widget.note_deleted.connect(self.delete_note)
                note_widget.note_copied.connect(self.copy_to_clipboard)
                self.notes_content_layout.addWidget(note_widget)
        
        # Add stretch to push items to top
        self.notes_content_layout.addStretch()
        
        # Refresh notes window if it's open
        if hasattr(self, 'notes_window') and self.notes_window and not self.notes_window.isHidden():
            self.notes_window.refresh_all_notes()
    
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
                self.add_note(None, selected_text, 1)  # No title, priority 1 for clipboard notes
                
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
                    self.add_note(None, original_clipboard, 1)  # No title, priority 1 for clipboard notes
    
    def open_all_notes(self):
        """
        Open a new window to display all notes in a larger, more readable format.
        """
        # If window already exists and is visible, just bring it to front
        if self.notes_window and not self.notes_window.isHidden():
            self.notes_window.raise_()
            self.notes_window.activateWindow()
            # Refresh notes when bringing to front
            self.notes_window.refresh_all_notes()
            return
        
        # Create new window or show existing one
        if not self.notes_window:
            self.notes_window = NotesWindow(self)
        
        self.notes_window.set_database_manager(self.database_manager)
        if hasattr(self.notes_window, 'set_openai_manager') and self.openai_manager:
            self.notes_window.set_openai_manager(self.openai_manager)
        if hasattr(self.notes_window, 'set_clipboard_manager') and self.clipboard_manager:
            self.notes_window.set_clipboard_manager(self.clipboard_manager)
        self.notes_window.show()
        self.notes_window.raise_()
        self.notes_window.activateWindow()
    
    def open_settings(self):
        """
        Open the settings window to configure dashboard features and layout.
        """
        # If window already exists and is visible, just bring it to front
        if self.settings_window and not self.settings_window.isHidden():
            self.settings_window.raise_()
            self.settings_window.activateWindow()
            return
        
        # Create new window or show existing one
        if not self.settings_window:
            self.settings_window = SettingsWindow(self)
            self.settings_window.settings_changed.connect(self.on_settings_changed)
        
        self.settings_window.show()
        self.settings_window.raise_()
        self.settings_window.activateWindow()
    
    def on_settings_changed(self, new_settings):
        """
        Handle settings changes from the settings window.
        
        Args:
            new_settings (dict): The new settings configuration
        """
        print("Settings changed, applying new configuration...")
        print(f"New settings: {new_settings}")
        
        # Reload config to get updated settings
        self.reload_config()
        
        # Rebuild the dashboard with new settings
        self.rebuild_dashboard(new_settings)
    
    def reload_config(self):
        """
        Reload the config module to get updated settings.
        """
        try:
            import importlib
            import config
            importlib.reload(config)
            print("Config reloaded successfully")
        except Exception as e:
            print(f"Error reloading config: {e}")
    
    def get_smart_response_visibility(self):
        """
        Get the smart response visibility setting from config.
        
        Returns:
            str: The visibility mode ('hidden' or 'popup')
        """
        try:
            import config
            return getattr(config, 'SMART_RESPONSE_VISIBILITY', 'popup')
        except Exception as e:
            print(f"Error getting smart response visibility: {e}")
            return 'popup'
    
    def rebuild_dashboard(self, settings):
        """
        Rebuild the dashboard based on the provided settings.
        
        Args:
            settings (dict): The settings configuration
        """
        # Store current managers
        clipboard_manager = self.clipboard_manager
        database_manager = self.database_manager
        openai_manager = self.openai_manager
        
        # Stop refresh timer to prevent accessing deleted UI elements
        if hasattr(self, 'refresh_timer'):
            self.refresh_timer.stop()
            self.refresh_timer.deleteLater()
        
        # Clear current UI elements to prevent access after deletion
        self.clipboard_content_layout = None
        self.notes_content_layout = None
        
        # Clear current UI
        central_widget = self.centralWidget()
        if central_widget:
            central_widget.deleteLater()
        
        # Rebuild UI with new settings
        self.setup_ui_with_settings(settings)
        
        # Adjust dashboard width based on number of columns
        self.adjust_dashboard_size(settings)
        
        # Restore managers
        self.set_managers(clipboard_manager, database_manager, openai_manager)
        
        # Create new refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_clipboard_history)
        self.refresh_timer.start(config.REFRESH_INTERVAL)
        
        print("Dashboard rebuilt with new settings")
    
    def setup_ui_with_settings(self, settings):
        """
        Set up the user interface based on the provided settings.
        
        Args:
            settings (dict): The settings configuration
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
        main_layout.setContentsMargins(8, 8, 8, 8)
        main_layout.setSpacing(8)
        
        # Header layout
        header_layout = QHBoxLayout()
        
        # Settings button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setMaximumWidth(30)
        self.settings_btn.setMaximumHeight(24)
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        
        header_layout.addWidget(self.settings_btn)
        header_layout.addStretch()
        
        # Add header to main layout first
        main_layout.addLayout(header_layout)
        
        # Create layout based on settings
        if settings['columns'] == 1:
            # Single column layout
            self.create_single_column_layout(main_layout, settings)
        elif settings['columns'] == 2:
            # Two column layout
            self.create_two_column_layout(main_layout, settings)
        else:
            # Three column layout
            self.create_three_column_layout(main_layout, settings)
        
        central_widget.setLayout(main_layout)
    
    def create_single_column_layout(self, main_layout, settings):
        """
        Create a single column layout.
        
        Args:
            main_layout: The main layout to add widgets to
            settings (dict): The settings configuration
        """
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
        
        # Add enabled features to splitter
        enabled_features = [f for f in settings['features'] if f['enabled']]
        enabled_features.sort(key=lambda x: x['order'])
        
        for feature in enabled_features:
            frame = self.create_feature_frame(feature)
            if frame:
                splitter.addWidget(frame)
        
        # Set initial sizes
        if enabled_features:
            size_per_feature = 200
            splitter.setSizes([size_per_feature] * len(enabled_features))
        
        main_layout.addWidget(splitter)
    
    def create_two_column_layout(self, main_layout, settings):
        """
        Create a two column layout.
        
        Args:
            main_layout: The main layout to add widgets to
            settings (dict): The settings configuration
        """
        # Create horizontal layout for two columns
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(8)
        
        # Create two vertical splitters
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        for splitter in [left_splitter, right_splitter]:
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
        
        # Add enabled features to splitters
        enabled_features = [f for f in settings['features'] if f['enabled']]
        enabled_features.sort(key=lambda x: x['order'])
        
        max_features_per_column = settings['max_features_per_column']
        
        for i, feature in enumerate(enabled_features):
            frame = self.create_feature_frame(feature)
            if frame:
                if i < max_features_per_column:
                    left_splitter.addWidget(frame)
                else:
                    right_splitter.addWidget(frame)
        
        # Set initial sizes for splitters
        if enabled_features:
            size_per_feature = 200
            left_count = min(len(enabled_features), max_features_per_column)
            right_count = max(0, len(enabled_features) - max_features_per_column)
            
            left_splitter.setSizes([size_per_feature] * left_count)
            right_splitter.setSizes([size_per_feature] * right_count)
        
        columns_layout.addWidget(left_splitter)
        columns_layout.addWidget(right_splitter)
        
        main_layout.addLayout(columns_layout)
    
    def create_three_column_layout(self, main_layout, settings):
        """
        Create a three column layout.
        
        Args:
            main_layout: The main layout to add widgets to
            settings (dict): The settings configuration
        """
        # Create horizontal layout for three columns
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(8)
        
        # Create three vertical splitters
        left_splitter = QSplitter(Qt.Orientation.Vertical)
        middle_splitter = QSplitter(Qt.Orientation.Vertical)
        right_splitter = QSplitter(Qt.Orientation.Vertical)
        
        for splitter in [left_splitter, middle_splitter, right_splitter]:
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
        
        # Add enabled features to splitters
        enabled_features = [f for f in settings['features'] if f['enabled']]
        enabled_features.sort(key=lambda x: x['order'])
        
        max_features_per_column = settings['max_features_per_column']
        
        for i, feature in enumerate(enabled_features):
            frame = self.create_feature_frame(feature)
            if frame:
                if i < max_features_per_column:
                    left_splitter.addWidget(frame)
                elif i < max_features_per_column * 2:
                    middle_splitter.addWidget(frame)
                else:
                    right_splitter.addWidget(frame)
        
        # Set initial sizes for splitters
        if enabled_features:
            size_per_feature = 200
            left_count = min(len(enabled_features), max_features_per_column)
            middle_count = min(max(0, len(enabled_features) - max_features_per_column), max_features_per_column)
            right_count = max(0, len(enabled_features) - max_features_per_column * 2)
            
            left_splitter.setSizes([size_per_feature] * left_count)
            middle_splitter.setSizes([size_per_feature] * middle_count)
            right_splitter.setSizes([size_per_feature] * right_count)
        
        columns_layout.addWidget(left_splitter)
        columns_layout.addWidget(middle_splitter)
        columns_layout.addWidget(right_splitter)
        
        main_layout.addLayout(columns_layout)
    
    def create_feature_frame(self, feature):
        """
        Create a frame for a specific feature.
        
        Args:
            feature (dict): Feature configuration
            
        Returns:
            QFrame: The created frame or None if feature is not supported
        """
        feature_id = feature['id']
        
        if feature_id == 'clipboard':
            return self.create_clipboard_frame()
        elif feature_id == 'notes':
            return self.create_notes_frame()
        elif feature_id == 'prompt_enhancement':
            return self.create_prompt_frame()
        elif feature_id == 'smart_response':
            return self.create_smart_response_frame()
        
        return None
    
    def create_clipboard_frame(self):
        """
        Create the clipboard history frame.
        
        Returns:
            QFrame: The clipboard frame
        """
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
        clipboard_layout.setSpacing(6)
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
        self.clipboard_content_layout.setSpacing(2)
        self.clipboard_content_layout.setContentsMargins(2, 2, 2, 2)
        self.clipboard_content.setLayout(self.clipboard_content_layout)
        self.clipboard_scroll.setWidget(self.clipboard_content)
        
        clipboard_layout.addWidget(self.clipboard_scroll)
        clipboard_frame.setLayout(clipboard_layout)
        
        return clipboard_frame
    
    def create_notes_frame(self):
        """
        Create the notes frame.
        
        Returns:
            QFrame: The notes frame
        """

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
        notes_layout.setSpacing(6)
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
        
        # Add Note button
        self.add_note_btn = QPushButton("Add")
        self.add_note_btn.setMaximumWidth(50)
        self.add_note_btn.setMaximumHeight(24)
        self.add_note_btn.clicked.connect(self.show_add_note_dialog)
        self.add_note_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
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
        notes_header_layout.addWidget(self.add_note_btn)
        notes_header_layout.addWidget(self.open_notes_btn)
        
        notes_layout.addLayout(notes_header_layout)
        
        # Search and Sort section
        search_sort_layout = QHBoxLayout()
        search_sort_layout.setSpacing(6)
        
        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search notes...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QLineEdit:focus {
                border-color: #4a90e2;
            }
        """)
        self.search_input.textChanged.connect(self.refresh_notes)
        
        # Sort dropdown
        self.sort_combo = QComboBox()
        self.sort_combo.addItems([
            "Updated (newest)",
            "Updated (oldest)", 
            "Created (newest)",
            "Created (oldest)",
            "Priority (high)",
            "Priority (low)",
            "Title (A-Z)",
            "Title (Z-A)"
        ])
        self.sort_combo.setCurrentIndex(0)
        self.sort_combo.setMaximumWidth(120)
        self.sort_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
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
        self.sort_combo.currentTextChanged.connect(self.refresh_notes)
        
        search_sort_layout.addWidget(self.search_input)
        search_sort_layout.addWidget(self.sort_combo)
        notes_layout.addLayout(search_sort_layout)
        
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
        self.notes_content_layout.setSpacing(2)
        self.notes_content_layout.setContentsMargins(2, 2, 2, 2)

        self.notes_content.setLayout(self.notes_content_layout)
        self.notes_scroll.setWidget(self.notes_content)
        
        notes_layout.addWidget(self.notes_scroll)
        notes_frame.setLayout(notes_layout)
        

        return notes_frame
    
    def create_prompt_frame(self):
        """
        Create the prompt enhancement frame.
        
        Returns:
            QFrame: The prompt frame or None if OpenAI is not enabled
        """
        import config
        if not config.OPENAI_ENABLED:
            return None
        
        prompt_frame = QFrame()
        prompt_frame.setFrameStyle(QFrame.Shape.Box)
        prompt_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: #ffffff;
                padding: 4px;
            }
        """)
        prompt_layout = QVBoxLayout()
        prompt_layout.setSpacing(6)
        prompt_layout.setContentsMargins(6, 6, 6, 6)
        
        # Prompt header
        prompt_header_layout = QHBoxLayout()
        prompt_header_layout.setSpacing(10)
        
        prompt_title = QLabel("🤖 AI Prompt Enhancement")
        prompt_title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 13px;
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
                font-size: 11px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        prompt_layout.addWidget(prompt_input_label)
        
        self.prompt_input = QTextEdit()
        self.prompt_input.setMaximumHeight(80)
        self.prompt_input.setPlaceholderText("Paste your prompt here and click 'Enhance' to get an improved version...")
        self.prompt_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QTextEdit:focus {
                border-color: #4a90e2;
            }
        """)
        prompt_layout.addWidget(self.prompt_input)
        
        # Loading spinner
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
                padding: 8px;
                font-size: 12px;
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
                font-size: 11px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        prompt_layout.addWidget(enhanced_label)
        
        self.enhanced_prompt_display = QTextEdit()
        self.enhanced_prompt_display.setMaximumHeight(120)
        self.enhanced_prompt_display.setReadOnly(True)
        self.enhanced_prompt_display.setPlaceholderText("Enhanced prompt will appear here...")
        self.enhanced_prompt_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
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
                padding: 6px;
                font-size: 11px;
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
                font-size: 10px;
                font-style: italic;
                background: transparent;
                padding: 2px;
            }
        """)
        prompt_layout.addWidget(self.status_label)
        
        prompt_frame.setLayout(prompt_layout)
        
        return prompt_frame
    
    def create_smart_response_frame(self):
        """
        Create the smart response frame.
        
        Returns:
            QFrame: The smart response frame or None if OpenAI is not enabled
        """
        import config
        if not config.OPENAI_ENABLED or not config.SMART_RESPONSE_ENABLED:
            return None
        
        smart_response_frame = QFrame()
        smart_response_frame.setFrameStyle(QFrame.Shape.Box)
        smart_response_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 6px;
                background: #ffffff;
                padding: 4px;
            }
        """)
        smart_response_layout = QVBoxLayout()
        smart_response_layout.setSpacing(6)
        smart_response_layout.setContentsMargins(6, 6, 6, 6)
        
        # Smart response header
        smart_response_header_layout = QHBoxLayout()
        smart_response_header_layout.setSpacing(10)
        
        smart_response_title = QLabel("🧠 AI Smart Response")
        smart_response_title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 13px;
                color: #2c3e50;
                margin-bottom: 2px;
                background: transparent;
            }
        """)
        
        smart_response_header_layout.addWidget(smart_response_title)
        smart_response_header_layout.addStretch()
        
        smart_response_layout.addLayout(smart_response_header_layout)
        
        # Smart response input area
        smart_response_input_label = QLabel("Enter your question, code, or prompt:")
        smart_response_input_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        smart_response_layout.addWidget(smart_response_input_label)
        
        self.smart_response_input = QTextEdit()
        self.smart_response_input.setMaximumHeight(80)
        self.smart_response_input.setPlaceholderText("Ask a question, paste code for review, or enter any prompt for AI response...")
        self.smart_response_input.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                background-color: #ffffff;
                color: #2c3e50;
            }
            QTextEdit:focus {
                border-color: #4a90e2;
            }
        """)
        smart_response_layout.addWidget(self.smart_response_input)
        
        # Smart response loading spinner
        self.smart_response_loading_spinner = LoadingSpinner()
        smart_response_layout.addWidget(self.smart_response_loading_spinner)
        
        # Generate response button
        self.generate_response_btn = QPushButton("Generate Response")
        self.generate_response_btn.clicked.connect(self.generate_smart_response)
        self.generate_response_btn.setStyleSheet("""
            QPushButton {
                background: #9b59b6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
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
        smart_response_layout.addWidget(self.generate_response_btn)
        
        # Generated response display
        generated_response_label = QLabel("AI Response:")
        generated_response_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        smart_response_layout.addWidget(generated_response_label)
        
        self.generated_response_display = QTextEdit()
        self.generated_response_display.setMaximumHeight(120)
        self.generated_response_display.setReadOnly(True)
        self.generated_response_display.setPlaceholderText("AI response will appear here...")
        self.generated_response_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 6px;
                font-size: 12px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)
        smart_response_layout.addWidget(self.generated_response_display)
        
        # Copy generated response button
        self.copy_response_btn = QPushButton("Copy Response")
        self.copy_response_btn.clicked.connect(self.copy_generated_response)
        self.copy_response_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
                font-size: 11px;
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
        smart_response_layout.addWidget(self.copy_response_btn)
        
        # Status label for feedback
        self.smart_response_status_label = QLabel("")
        self.smart_response_status_label.setStyleSheet("""
            QLabel {
                color: #27ae60;
                font-size: 10px;
                font-style: italic;
                background: transparent;
                padding: 2px;
            }
        """)
        smart_response_layout.addWidget(self.smart_response_status_label)
        
        smart_response_frame.setLayout(smart_response_layout)
        
        return smart_response_frame
    
    def adjust_dashboard_size(self, settings):
        """
        Adjust the dashboard size based on the number of columns.
        
        Args:
            settings (dict): The settings configuration
        """
        import config
        
        # Base width for single column
        base_width = config.DASHBOARD_WIDTH
        
        # Calculate new width based on number of columns
        columns = settings['columns']
        if columns == 1:
            new_width = base_width
        elif columns == 2:
            # Two columns: increase width by 60%
            new_width = int(base_width * 1.6)
        else:  # 3 columns
            # Three columns: increase width by 120%
            new_width = int(base_width * 2.2)
        
        # Set new size
        self.resize(new_width, config.DASHBOARD_HEIGHT)
        
        # Reposition window to stay on the right side
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        x = screen_geometry.width() - new_width - config.DASHBOARD_POSITION_X_OFFSET
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        print(f"Dashboard size adjusted: {new_width}x{config.DASHBOARD_HEIGHT} ({columns} columns)")
    
    def load_and_apply_settings(self):
        """
        Load settings and apply them to the dashboard.
        """
        try:
            from .settings import SettingsWindow
            # Create a temporary settings window to load settings
            temp_settings = SettingsWindow()
            settings = temp_settings.get_settings()
            temp_settings.close()
            
            # Apply settings
            self.rebuild_dashboard(settings)
            print("Settings loaded and applied successfully")
        except Exception as e:
            print(f"Error loading settings: {e}")
            # Continue with default layout
            self.setup_ui()
    
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
    
    def enhance_prompt_from_clipboard_safe(self):
        """
        Thread-safe version of enhance_prompt_from_clipboard.
        
        This method emits the enhance_prompt_from_clipboard_signal to trigger the
        prompt enhancement hotkey from a different thread.
        """
        self.enhance_prompt_from_clipboard_signal.emit()
    
    def generate_smart_response_from_clipboard_safe(self):
        """
        Thread-safe version of generate_smart_response_from_clipboard.
        
        This method emits the generate_smart_response_from_clipboard_signal to trigger the
        smart response hotkey from a different thread.
        """
        self.generate_smart_response_from_clipboard_signal.emit()
    
    # =============================================================================
    # OPENAI PROMPT ENHANCEMENT METHODS
    # =============================================================================
    
    def enhance_prompt(self):
        """
        Enhance the prompt in the input field using OpenAI API.
        """
        if not self.openai_manager:
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
        if self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(enhanced_prompt)
            print(f"Enhanced prompt automatically copied to clipboard: {enhanced_prompt[:50]}...")
        
        # Replace the original prompt with the enhanced version
        self.prompt_input.setPlainText(enhanced_prompt)
        
        # Automatically paste the enhanced text to replace selected text
        import keyboard
        import time
        time.sleep(0.1)  # Small delay to ensure clipboard is ready
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
        if enhanced_text and self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(enhanced_text)
            print("Enhanced prompt copied to clipboard")
            
            # Show feedback for manual copy
            self.status_label.setText("✓ Enhanced prompt copied to clipboard")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.status_label.setText(""))
    
    def enhance_prompt_from_clipboard(self):
        """
        Enhance a prompt from the currently selected text.
        
        This method is called when the user triggers the "Enhance prompt from clipboard"
        hotkey. It saves the current clipboard content, simulates a Ctrl+C key
        press to copy the selected text, and then attempts to enhance it using OpenAI.
        """
        print("Enhance prompt from selected text hotkey triggered!")
        
        if not self.openai_manager:
            QMessageBox.warning(self, "OpenAI Not Available", 
                              "OpenAI features are not enabled or configured.")
            return
        
        if not self.clipboard_manager:
            QMessageBox.warning(self, "Clipboard Not Available", 
                              "Clipboard manager not available.")
            return
        
        # Import keyboard module for simulating key presses
        import keyboard
        import time
        
        # Save current clipboard content
        original_clipboard = self.clipboard_manager.get_current_clipboard()
        print(f"Original clipboard saved: {original_clipboard[:30] if original_clipboard else 'None'}...")
        
        # Simulate Ctrl+C to copy selected text
        keyboard.send('ctrl+c')
        time.sleep(0.2)  # Longer delay to ensure copy completes
        
        # Get the newly copied text (selected text)
        selected_text = self.clipboard_manager.get_current_clipboard()
        print(f"Selected text: '{selected_text[:50]}...' (length: {len(selected_text) if selected_text else 0})")
        
        # Additional validation: check if the selected text is meaningful
        if selected_text and len(selected_text.strip()) < 2:
            print("Selected text too short - likely not meaningful selection")
            QMessageBox.warning(self, "Invalid Selection", 
                              "Please select more text (at least 2 characters) before using Ctrl+Alt+E.")
            return
        
        # Check if we actually got new text and it's different from original
        if not selected_text:
            print("No text selected - clipboard is empty")
            QMessageBox.warning(self, "No Text Selected", 
                              "Please select some text before using Ctrl+Alt+E to enhance it.")
            return
        
        if selected_text == original_clipboard:
            print("Selected text is same as clipboard - likely no selection")
            QMessageBox.warning(self, "No Text Selected", 
                              "Please select some text before using Ctrl+Alt+E to enhance it.")
            return
        
        # Show loading message
        self.show_enhancement_loading_message()
        
        # Create and start worker thread for enhancement
        self.openai_worker = OpenAIWorker(self.openai_manager, selected_text)
        self.openai_worker.enhancement_complete.connect(self.on_enhancement_complete_with_replacement)
        self.openai_worker.enhancement_failed.connect(self.on_enhancement_failed_silent)
        self.openai_worker.finished.connect(self.on_worker_finished_silent)
        self.openai_worker.start()
    
    def show_enhancement_loading_message(self):
        """
        Show a loading message for clipboard enhancement.
        """
        # Create a floating loading widget instead of a modal dialog
        self.loading_widget = QWidget()
        self.loading_widget.setWindowTitle("Enhancing Prompt")
        self.loading_widget.setFixedSize(250, 80)
        self.loading_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.loading_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create the main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create a styled container
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: rgba(52, 73, 94, 0.95);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(15, 15, 15, 15)
        
        # Loading label with spinner
        loading_layout = QHBoxLayout()
        
        # Spinner dots
        self.spinner_label = QLabel("⠋")
        self.spinner_label.setStyleSheet("""
            QLabel {
                color: #e67e22;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Loading text
        self.loading_label = QLabel("Enhancing selected text...")
        self.loading_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        loading_layout.addWidget(self.spinner_label)
        loading_layout.addWidget(self.loading_label)
        loading_layout.addStretch()
        
        container_layout.addLayout(loading_layout)
        container.setLayout(container_layout)
        layout.addWidget(container)
        self.loading_widget.setLayout(layout)
        
        # Position the widget near the cursor
        cursor_pos = self.cursor().pos()
        screen_geometry = self.screen().geometry()
        
        # Calculate position to ensure widget stays on screen
        x = min(max(cursor_pos.x() - 125, 10), screen_geometry.width() - 260)
        y = min(max(cursor_pos.y() - 40, 10), screen_geometry.height() - 90)
        
        self.loading_widget.move(x, y)
        
        # Timer for updating loading animation
        self.loading_timer = QTimer()
        self.loading_timer.timeout.connect(self.update_loading_animation)
        self.loading_timer.start(100)
        
        # Animation state
        self.current_dot = 0
        self.dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        # Show the widget
        self.loading_widget.show()
    
    def update_loading_animation(self):
        """
        Update the loading animation.
        """
        # Update spinner animation
        self.current_dot = (self.current_dot + 1) % len(self.dots)
        self.spinner_label.setText(self.dots[self.current_dot])
        
        # Simple text animation
        current_text = self.loading_label.text()
        if current_text.endswith("..."):
            self.loading_label.setText("Enhancing selected text")
        else:
            self.loading_label.setText(current_text + ".")
    
    def on_enhancement_complete_with_replacement(self, enhanced_text):
        """
        Handle successful clipboard enhancement with clipboard replacement.
        
        Args:
            enhanced_text (str): The enhanced text
        """
        if self.clipboard_manager:
            # Copy enhanced text to clipboard
            self.clipboard_manager.copy_to_clipboard(enhanced_text)
            print(f"Enhanced text copied to clipboard: {enhanced_text[:50]}...")
        
        # Automatically paste the enhanced text to replace selected text
        import keyboard
        import time
        time.sleep(0.2)  # Slightly longer delay to ensure clipboard is ready and user sees the process
        keyboard.send('ctrl+v')
        print("Enhanced text automatically pasted to replace selected text")
        
        # Close loading dialog
        self.close_enhancement_loading_message()
    
    def on_enhancement_failed_silent(self, error_message):
        """
        Handle failed clipboard enhancement silently.
        
        Args:
            error_message (str): The error message
        """
        print(f"Silent enhancement failed: {error_message}")
        # Close loading dialog
        self.close_enhancement_loading_message()
    
    def on_worker_finished_silent(self):
        """
        Handle silent worker thread completion.
        """
        print("Silent OpenAI worker finished")
    
    def close_enhancement_loading_message(self):
        """
        Close the enhancement loading message.
        """
        if hasattr(self, 'loading_timer'):
            self.loading_timer.stop()
        if hasattr(self, 'loading_widget'):
            self.loading_widget.close()
            self.loading_widget = None
    
    def force_close_loading_message(self):
        """
        Force close the loading message (for cleanup).
        """
        self.close_enhancement_loading_message() 
    
    # =============================================================================
    # SMART RESPONSE GENERATION METHODS
    # =============================================================================
    
    def generate_smart_response(self):
        """
        Generate a smart response to the user input using OpenAI API.
        """
        if not self.openai_manager:
            QMessageBox.warning(self, "OpenAI Not Available", 
                              "OpenAI features are not enabled or configured.")
            return
        
        # Get the user input
        user_input = self.smart_response_input.toPlainText().strip()
        
        if not user_input:
            QMessageBox.warning(self, "No Input", 
                              "Please enter some text to generate a response for.")
            return
        
        # Check smart response visibility setting
        visibility_mode = self.get_smart_response_visibility()
        
        if visibility_mode == 'hidden':
            # Hidden mode: no visual feedback, just generate and copy
            print("Smart response in hidden mode - generating without visual feedback")
            self.smart_response_worker = SmartResponseWorker(self.openai_manager, user_input, "general")
            self.smart_response_worker.response_complete.connect(self.on_smart_response_complete_hidden_ui)
            self.smart_response_worker.response_failed.connect(self.on_smart_response_failed_hidden_ui)
            self.smart_response_worker.finished.connect(self.on_smart_response_worker_finished_hidden_ui)
            self.smart_response_worker.start()
        else:
            # Popup mode: show loading and popup
            # Show loading spinner and disable button
            self.smart_response_loading_spinner.start_animation()
            self.generate_response_btn.setEnabled(False)
            self.generate_response_btn.setText("Generating...")
            self.copy_response_btn.setEnabled(False)
            
            # Create and start worker thread
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
        # Display the generated response in the UI
        self.generated_response_display.setPlainText(generated_response)
        self.copy_response_btn.setEnabled(True)
        
        # Show popup with response
        from .components import SmartResponsePopup
        self.smart_response_popup = SmartResponsePopup(generated_response, self)
        self.smart_response_popup.set_clipboard_manager(self.clipboard_manager)
        self.smart_response_popup.show()
        
        # Show success status message
        self.smart_response_status_label.setText("✓ Generated response popup shown")
        
        # Clear status message after 3 seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.smart_response_status_label.setText(""))
        
        print(f"Smart response generation completed successfully: {generated_response[:50]}...")
        print("Response popup shown")
    
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
        self.generate_response_btn.setEnabled(True)
        self.generate_response_btn.setText("Generate Response")
        print("Smart response worker finished")
    
    def copy_generated_response(self):
        """
        Copy the generated response to the clipboard.
        """
        response_text = self.generated_response_display.toPlainText()
        if response_text and self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(response_text)
            print("Generated response copied to clipboard")
            
            # Show feedback for manual copy
            self.smart_response_status_label.setText("✓ Generated response copied to clipboard")
            from PyQt6.QtCore import QTimer
            QTimer.singleShot(2000, lambda: self.smart_response_status_label.setText(""))
    
    def generate_smart_response_from_clipboard(self):
        """
        Generate a smart response from the currently selected text.
        
        This method is called when the user triggers the "Generate smart response from clipboard"
        hotkey. It saves the current clipboard content, simulates a Ctrl+C key
        press to copy the selected text, and then attempts to generate a smart response using OpenAI.
        """
        print("Generate smart response from selected text hotkey triggered!")
        
        if not self.openai_manager:
            QMessageBox.warning(self, "OpenAI Not Available", 
                              "OpenAI features are not enabled or configured.")
            return
        
        if not self.clipboard_manager:
            QMessageBox.warning(self, "Clipboard Not Available", 
                              "Clipboard manager not available.")
            return
        
        # Import keyboard module for simulating key presses
        import keyboard
        import time
        
        # Save current clipboard content
        original_clipboard = self.clipboard_manager.get_current_clipboard()
        print(f"Original clipboard saved: {original_clipboard[:30] if original_clipboard else 'None'}...")
        
        # Simulate Ctrl+C to copy selected text
        keyboard.send('ctrl+c')
        time.sleep(0.2)  # Longer delay to ensure copy completes
        
        # Get the newly copied text (selected text)
        selected_text = self.clipboard_manager.get_current_clipboard()
        print(f"Selected text: '{selected_text[:50]}...' (length: {len(selected_text) if selected_text else 0})")
        
        # Additional validation: check if the selected text is meaningful
        if selected_text and len(selected_text.strip()) < 2:
            print("Selected text too short - likely not meaningful selection")
            QMessageBox.warning(self, "Invalid Selection", 
                              "Please select more text (at least 2 characters) before using Ctrl+Alt+R.")
            return
        
        # Check if we actually got new text and it's different from original
        if not selected_text:
            print("No text selected - clipboard is empty")
            QMessageBox.warning(self, "No Text Selected", 
                              "Please select some text before using Ctrl+Alt+R to generate a response.")
            return
        
        if selected_text == original_clipboard:
            print("Selected text is same as clipboard - likely no selection")
            QMessageBox.warning(self, "No Text Selected", 
                              "Please select some text before using Ctrl+Alt+R to generate a response.")
            return
        
        # Check smart response visibility setting
        visibility_mode = self.get_smart_response_visibility()
        
        if visibility_mode == 'hidden':
            # Hidden mode: no visual feedback, just generate and copy
            print("Smart response in hidden mode - generating without visual feedback")
            self.smart_response_worker = SmartResponseWorker(self.openai_manager, selected_text, "general")
            self.smart_response_worker.response_complete.connect(self.on_smart_response_complete_hidden)
            self.smart_response_worker.response_failed.connect(self.on_smart_response_failed_hidden)
            self.smart_response_worker.finished.connect(self.on_smart_response_worker_finished_hidden)
            self.smart_response_worker.start()
        else:
            # Popup mode: show loading and popup
            self.show_smart_response_loading_message()
            self.smart_response_worker = SmartResponseWorker(self.openai_manager, selected_text, "general")
            self.smart_response_worker.response_complete.connect(self.on_smart_response_complete_with_replacement)
            self.smart_response_worker.response_failed.connect(self.on_smart_response_failed_silent)
            self.smart_response_worker.finished.connect(self.on_smart_response_worker_finished_silent)
            self.smart_response_worker.start()
    
    def show_smart_response_loading_message(self):
        """
        Show a loading message for smart response generation.
        """
        # Create a floating loading widget instead of a modal dialog
        self.smart_response_loading_widget = QWidget()
        self.smart_response_loading_widget.setWindowTitle("Generating Response")
        self.smart_response_loading_widget.setFixedSize(250, 80)
        self.smart_response_loading_widget.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.smart_response_loading_widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Create the main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Create a styled container
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background: rgba(155, 89, 182, 0.95);
                border-radius: 8px;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
        """)
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(15, 15, 15, 15)
        
        # Loading label with spinner
        loading_layout = QHBoxLayout()
        
        # Spinner dots
        self.smart_response_spinner_label = QLabel("⠋")
        self.smart_response_spinner_label.setStyleSheet("""
            QLabel {
                color: #f39c12;
                font-size: 18px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        # Loading text
        self.smart_response_loading_label = QLabel("Generating smart response...")
        self.smart_response_loading_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 12px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        loading_layout.addWidget(self.smart_response_spinner_label)
        loading_layout.addWidget(self.smart_response_loading_label)
        loading_layout.addStretch()
        
        container_layout.addLayout(loading_layout)
        container.setLayout(container_layout)
        layout.addWidget(container)
        self.smart_response_loading_widget.setLayout(layout)
        
        # Position the widget near the cursor
        cursor_pos = self.cursor().pos()
        screen_geometry = self.screen().geometry()
        
        # Calculate position to ensure widget stays on screen
        x = min(max(cursor_pos.x() - 125, 10), screen_geometry.width() - 260)
        y = min(max(cursor_pos.y() - 40, 10), screen_geometry.height() - 90)
        
        self.smart_response_loading_widget.move(x, y)
        
        # Timer for updating loading animation
        self.smart_response_loading_timer = QTimer()
        self.smart_response_loading_timer.timeout.connect(self.update_smart_response_loading_animation)
        self.smart_response_loading_timer.start(100)
        
        # Animation state
        self.smart_response_current_dot = 0
        self.smart_response_dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        # Show the widget
        self.smart_response_loading_widget.show()
    
    def update_smart_response_loading_animation(self):
        """
        Update the smart response loading animation.
        """
        # Update spinner animation
        self.smart_response_current_dot = (self.smart_response_current_dot + 1) % len(self.smart_response_dots)
        self.smart_response_spinner_label.setText(self.smart_response_dots[self.smart_response_current_dot])
        
        # Simple text animation
        current_text = self.smart_response_loading_label.text()
        if current_text.endswith("..."):
            self.smart_response_loading_label.setText("Generating smart response")
        else:
            self.smart_response_loading_label.setText(current_text + ".")
    
    def on_smart_response_complete_with_replacement(self, generated_response):
        """
        Handle successful smart response generation with clipboard replacement.
        
        Args:
            generated_response (str): The generated response
        """
        # Close loading dialog
        self.close_smart_response_loading_message()
        
        # Show popup with response
        from .components import SmartResponsePopup
        self.smart_response_popup = SmartResponsePopup(generated_response, self)
        self.smart_response_popup.set_clipboard_manager(self.clipboard_manager)
        self.smart_response_popup.show()
        
        print(f"Smart response popup shown with: {generated_response[:50]}...")
    
    def on_smart_response_failed_silent(self, error_message):
        """
        Handle failed smart response generation silently.
        
        Args:
            error_message (str): The error message
        """
        print(f"Silent smart response generation failed: {error_message}")
        # Close loading dialog
        self.close_smart_response_loading_message()
    
    def on_smart_response_worker_finished_silent(self):
        """
        Handle silent smart response worker thread completion.
        """
        print("Silent smart response worker finished")
    
    def close_smart_response_loading_message(self):
        """
        Close the smart response loading message.
        """
        if hasattr(self, 'smart_response_loading_timer'):
            self.smart_response_loading_timer.stop()
        if hasattr(self, 'smart_response_loading_widget'):
            self.smart_response_loading_widget.close()
            self.smart_response_loading_widget = None
    
    def on_smart_response_complete_hidden(self, generated_response):
        """
        Handle successful smart response generation in hidden mode.
        
        Args:
            generated_response (str): The generated response
        """
        if self.clipboard_manager:
            # Copy generated response to clipboard
            self.clipboard_manager.copy_to_clipboard(generated_response)
            print(f"Generated response copied to clipboard (hidden mode): {generated_response[:50]}...")
        
        # Automatically paste the generated response to replace selected text
        import keyboard
        import time
        time.sleep(0.2)  # Slightly longer delay to ensure clipboard is ready
        keyboard.send('ctrl+v')
        print("Generated response automatically pasted to replace selected text (hidden mode)")
    
    def on_smart_response_failed_hidden(self, error_message):
        """
        Handle failed smart response generation in hidden mode.
        
        Args:
            error_message (str): The error message
        """
        print(f"Hidden smart response generation failed: {error_message}")
    
    def on_smart_response_worker_finished_hidden(self):
        """
        Handle hidden smart response worker thread completion.
        """
        print("Hidden smart response worker finished")
    
    def on_smart_response_complete_hidden_ui(self, generated_response):
        """
        Handle successful smart response generation in hidden mode (UI).
        
        Args:
            generated_response (str): The generated response
        """
        # Display the generated response in the UI
        self.generated_response_display.setPlainText(generated_response)
        self.copy_response_btn.setEnabled(True)
        
        # Automatically copy the generated response to clipboard
        if self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(generated_response)
            print(f"Generated response automatically copied to clipboard (hidden UI mode): {generated_response[:50]}...")
        
        # Replace the original input with the generated response
        self.smart_response_input.setPlainText(generated_response)
        
        # Show success status message
        self.smart_response_status_label.setText("✓ Generated response copied to clipboard")
        
        # Clear status message after 3 seconds
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: self.smart_response_status_label.setText(""))
        
        print(f"Smart response generation completed successfully (hidden UI mode): {generated_response[:50]}...")
    
    def on_smart_response_failed_hidden_ui(self, error_message):
        """
        Handle failed smart response generation in hidden mode (UI).
        
        Args:
            error_message (str): The error message
        """
        QMessageBox.warning(self, "Response Generation Failed", 
                          f"Failed to generate response: {error_message}")
        print(f"Response generation failed (hidden UI mode): {error_message}")
    
    def on_smart_response_worker_finished_hidden_ui(self):
        """
        Handle hidden smart response worker thread completion (UI).
        """
        print("Hidden smart response worker finished (UI)")