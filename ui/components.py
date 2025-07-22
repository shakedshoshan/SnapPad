"""
UI Components for SnapPad

This module contains reusable UI components used throughout the application.
"""

import time
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTextEdit, QFrame, QApplication)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor


class LoadingSpinner(QWidget):
    """
    A simple loading spinner widget that shows an animated loading indicator.
    
    This widget displays a rotating circle animation to indicate that a process
    is running. It can be started and stopped as needed.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the loading spinner.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.setFixedSize(20, 20)
        self.angle = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        self.is_animating = False
        
        # Hide by default
        self.hide()
    
    def start_animation(self):
        """
        Start the loading animation.
        """
        self.angle = 0
        self.is_animating = True
        self.show()
        self.timer.start(50)  # Update every 50ms
    
    def stop_animation(self):
        """
        Stop the loading animation.
        """
        self.is_animating = False
        self.timer.stop()
        self.hide()
    
    def rotate(self):
        """
        Rotate the spinner by updating the angle.
        """
        if self.is_animating:
            self.angle = (self.angle + 30) % 360
            self.update()
    
    def paintEvent(self, event):
        """
        Paint the loading spinner.
        
        Args:
            event: Paint event
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Set up the pen and brush
        painter.setPen(QColor(52, 152, 219))  # Blue color
        painter.setBrush(QColor(52, 152, 219))
        
        # Calculate center and radius
        center_x = self.width() // 2
        center_y = self.height() // 2
        radius = min(center_x, center_y) - 2
        
        # Draw the spinner as a rotating arc
        painter.drawArc(center_x - radius, center_y - radius, 
                       radius * 2, radius * 2, 
                       self.angle * 16, 120 * 16)  # 120 degree arc


class SmartResponsePopup(QWidget):
    """
    A popup dialog for displaying smart response results.
    
    This widget shows the generated response with copy and exit buttons.
    It appears as a floating window that stays on top of other applications.
    """
    
    def __init__(self, response_text, parent=None):
        """
        Initialize the smart response popup.
        
        Args:
            response_text (str): The generated response text to display
            parent: Parent widget
        """
        super().__init__(parent)
        self.response_text = response_text
        self.clipboard_manager = None
        
        self.setup_ui()
        self.setup_window_properties()
    
    def setup_ui(self):
        """
        Set up the user interface for the popup.
        """
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Title
        title = QLabel("🧠 AI Smart Response")
        title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 14px;
                color: #2c3e50;
                background: transparent;
            }
        """)
        main_layout.addWidget(title)
        
        # Response display
        response_label = QLabel("Generated Response:")
        response_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        main_layout.addWidget(response_label)
        
        self.response_display = QTextEdit()
        self.response_display.setPlainText(self.response_text)
        self.response_display.setReadOnly(True)
        self.response_display.setMaximumHeight(200)
        self.response_display.setStyleSheet("""
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 8px;
                font-size: 12px;
                background-color: #f8f9fa;
                color: #2c3e50;
            }
        """)
        main_layout.addWidget(self.response_display)
        
        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)
        
        # Copy button
        self.copy_btn = QPushButton("Copy Response")
        self.copy_btn.clicked.connect(self.copy_response)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        # Exit button
        self.exit_btn = QPushButton("Exit")
        self.exit_btn.clicked.connect(self.close)
        self.exit_btn.setStyleSheet("""
            QPushButton {
                background: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #c0392b;
            }
        """)
        
        buttons_layout.addWidget(self.copy_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.exit_btn)
        
        main_layout.addLayout(buttons_layout)
        
        self.setLayout(main_layout)
    
    def setup_window_properties(self):
        """
        Configure window properties for the popup.
        """
        self.setWindowTitle("Smart Response")
        self.setFixedSize(400, 300)
        
        # Set window flags for floating behavior
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint | 
            Qt.WindowType.Tool | 
            Qt.WindowType.WindowStaysOnTopHint
        )
        
        # Center on screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Set styling
        self.setStyleSheet("""
            QWidget {
                background: #ffffff;
                border: 2px solid #9b59b6;
                border-radius: 8px;
            }
        """)
    
    def set_clipboard_manager(self, clipboard_manager):
        """
        Set the clipboard manager for copying responses.
        
        Args:
            clipboard_manager: The clipboard manager instance
        """
        self.clipboard_manager = clipboard_manager
    
    def copy_response(self):
        """
        Copy the response text to clipboard.
        """
        if self.clipboard_manager:
            self.clipboard_manager.copy_to_clipboard(self.response_text)
            print("Response copied to clipboard from popup")
            
            # Show feedback
            self.copy_btn.setText("Copied!")
            QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy Response"))
    
    def closeEvent(self, event):
        """
        Handle close event.
        
        Args:
            event: Close event
        """
        # Automatically copy to clipboard when closing if not already copied
        if self.clipboard_manager and not self.copy_btn.text() == "Copied!":
            self.clipboard_manager.copy_to_clipboard(self.response_text)
            print("Response automatically copied to clipboard on popup close")
        
        event.accept()


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