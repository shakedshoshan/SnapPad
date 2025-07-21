"""
Basic UI Components for SnapPad

This module contains basic UI components used throughout the application.
"""

from PyQt6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QFont


class LoadingSpinner(QWidget):
    """
    A custom loading spinner widget that shows animated dots.
    
    This widget displays a simple animated loading indicator with dots
    that cycle through to show that a process is running.
    """
    
    def __init__(self, parent=None):
        """
        Initialize the loading spinner.
        
        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        
        # Setup the UI
        self.setup_ui()
        
        # Animation state
        self.current_dot = 0
        self.dots = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
        # Timer for animation
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        self.animation_timer.setInterval(100)  # Update every 100ms
        
        # Initially hidden
        self.hide()
    
    def setup_ui(self):
        """
        Set up the user interface for the loading spinner.
        """
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        # Loading text
        self.loading_label = QLabel("Enhancing prompt")
        self.loading_label.setStyleSheet("""
            QLabel {
                color: #7f8c8d;
                font-size: 12px;
                background: transparent;
            }
        """)
        
        # Spinner dots
        self.spinner_label = QLabel("⠋")
        self.spinner_label.setStyleSheet("""
            QLabel {
                color: #e67e22;
                font-size: 16px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        layout.addWidget(self.loading_label)
        layout.addWidget(self.spinner_label)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def start_animation(self):
        """
        Start the loading animation.
        """
        self.current_dot = 0
        self.show()
        self.animation_timer.start()
    
    def stop_animation(self):
        """
        Stop the loading animation.
        """
        self.animation_timer.stop()
        self.hide()
    
    def update_animation(self):
        """
        Update the animation frame.
        """
        self.current_dot = (self.current_dot + 1) % len(self.dots)
        self.spinner_label.setText(self.dots[self.current_dot])


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