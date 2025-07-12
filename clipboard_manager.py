import pyperclip
import threading
import time
from typing import List, Optional, Callable
from collections import deque
import config


class ClipboardManager:
    """Manages clipboard monitoring and history for SnapPad."""
    
    def __init__(self, max_history: int = 10):
        self.max_history = max_history
        self.clipboard_history = deque(maxlen=max_history)
        self.current_clipboard = ""
        self.monitoring = False
        self.monitor_thread = None
        self.callbacks = []
        self._lock = threading.Lock()
    
    def add_callback(self, callback: Callable[[str], None]):
        """Add a callback to be called when clipboard changes."""
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str], None]):
        """Remove a callback."""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, new_content: str):
        """Notify all registered callbacks of clipboard change."""
        for callback in self.callbacks:
            try:
                callback(new_content)
            except Exception as e:
                print(f"Error in clipboard callback: {e}")
    
    def start_monitoring(self):
        """Start monitoring clipboard changes."""
        if self.monitoring:
            return
        
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.monitor_thread.start()
        print("Clipboard monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring clipboard changes."""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("Clipboard monitoring stopped")
    
    def _monitor_clipboard(self):
        """Monitor clipboard for changes (runs in background thread)."""
        # Initialize with current clipboard content
        try:
            self.current_clipboard = pyperclip.paste()
            if self.current_clipboard.strip():
                self._add_to_history(self.current_clipboard)
        except Exception as e:
            print(f"Error initializing clipboard: {e}")
        
        while self.monitoring:
            try:
                new_content = pyperclip.paste()
                
                # Check if clipboard content changed
                if new_content != self.current_clipboard:
                    self.current_clipboard = new_content
                    
                    # Only add non-empty text content
                    if new_content and new_content.strip():
                        self._add_to_history(new_content)
                        self._notify_callbacks(new_content)
                
                time.sleep(config.CLIPBOARD_MONITOR_INTERVAL)  # Check based on config
                
            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
                time.sleep(1)  # Wait longer on error
    
    def _add_to_history(self, content: str):
        """Add content to clipboard history."""
        with self._lock:
            # Remove duplicate if it exists
            try:
                self.clipboard_history.remove(content)
            except ValueError:
                pass  # Content not in history
            
            # Add to front of history
            self.clipboard_history.appendleft(content)
    
    def get_clipboard_history(self) -> List[str]:
        """Get the current clipboard history."""
        with self._lock:
            return list(self.clipboard_history)
    
    def copy_to_clipboard(self, content: str):
        """Copy content to clipboard."""
        try:
            pyperclip.copy(content)
            # Update our current clipboard tracking
            self.current_clipboard = content
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
    
    def get_current_clipboard(self) -> Optional[str]:
        """Get the current clipboard content."""
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error getting clipboard content: {e}")
            return None
    
    def clear_history(self):
        """Clear the clipboard history."""
        with self._lock:
            self.clipboard_history.clear()
    
    def get_history_item(self, index: int) -> Optional[str]:
        """Get a specific item from clipboard history by index."""
        with self._lock:
            if 0 <= index < len(self.clipboard_history):
                return self.clipboard_history[index]
            return None 