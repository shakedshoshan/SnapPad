"""
Background Worker Threads for SnapPad

This module contains background worker threads for handling time-consuming operations
without blocking the UI.
"""

from PyQt6.QtCore import QThread, pyqtSignal


class OpenAIWorker(QThread):
    """
    Background worker thread for OpenAI API calls.
    
    This thread handles the OpenAI API requests to prevent the UI from freezing
    during the API call. It emits signals when the request completes or fails.
    """
    
    # Signals for communicating with the main thread
    enhancement_complete = pyqtSignal(str)  # Emitted when enhancement succeeds
    enhancement_failed = pyqtSignal(str)    # Emitted when enhancement fails
    
    def __init__(self, openai_manager, prompt):
        """
        Initialize the worker thread.
        
        Args:
            openai_manager: The OpenAI manager instance
            prompt: The prompt to enhance
        """
        super().__init__()
        self.openai_manager = openai_manager
        self.prompt = prompt
    
    def run(self):
        """
        Run the enhancement in the background thread.
        """
        print(f"OpenAI worker starting with prompt: {self.prompt[:50]}...")
        try:
            enhanced_prompt = self.openai_manager.enhance_prompt(self.prompt)
            if enhanced_prompt:
                print(f"Enhancement successful, emitting signal with: {enhanced_prompt[:50]}...")
                self.enhancement_complete.emit(enhanced_prompt)
            else:
                print("Enhancement failed - no result returned")
                self.enhancement_failed.emit("Failed to enhance prompt")
        except Exception as e:
            print(f"Enhancement exception: {e}")
            self.enhancement_failed.emit(str(e)) 