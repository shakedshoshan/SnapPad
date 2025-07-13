"""
Clipboard Manager for SnapPad

This module handles clipboard monitoring and history management for the SnapPad application.
It provides real-time clipboard tracking, maintains a history of recent clipboard items,
and offers callback mechanisms for clipboard change notifications.

Key Features:
- Real-time clipboard monitoring in a background thread
- Configurable history size with automatic cleanup
- Duplicate detection and handling
- Thread-safe operations with proper locking
- Callback system for clipboard change notifications
- Graceful start/stop of monitoring services

The clipboard manager uses pyperclip for cross-platform clipboard access and
maintains clipboard history in memory using a deque for efficient operations.

Author: SnapPad Team
Version: 1.0.0
"""

import pyperclip
import threading
import time
from typing import List, Optional, Callable
from collections import deque
import config


class ClipboardManager:
    """
    Manages clipboard monitoring and history for SnapPad.
    
    This class provides comprehensive clipboard management including:
    - Background monitoring of clipboard changes
    - History management with configurable size limits
    - Duplicate detection and removal
    - Thread-safe operations
    - Callback notifications for clipboard changes
    - Graceful start/stop of monitoring services
    
    The clipboard history is stored in memory using a deque for efficient
    operations. The most recent items are kept at the front of the deque.
    
    Thread Safety:
    All clipboard operations are thread-safe using threading.Lock() to prevent
    race conditions between the monitoring thread and UI thread.
    """
    
    def __init__(self, max_history: int = 10):
        """
        Initialize the clipboard manager.
        
        Args:
            max_history (int): Maximum number of clipboard items to store in history.
                              Defaults to 10. When the limit is reached, oldest items
                              are automatically removed.
        """
        # Configuration
        self.max_history = max_history
        
        # Clipboard history storage using deque for efficient operations
        # deque automatically handles size limits and provides O(1) operations
        self.clipboard_history = deque(maxlen=max_history)
        
        # Current clipboard content tracking
        self.current_clipboard = ""
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Callback system for clipboard change notifications
        self.callbacks = []
        
        # Thread safety lock
        self._lock = threading.Lock()
    
    def add_callback(self, callback: Callable[[str], None]):
        """
        Add a callback function to be called when clipboard changes.
        
        Callbacks are called whenever new content is detected in the clipboard.
        This allows other parts of the application to react to clipboard changes.
        
        Args:
            callback (Callable[[str], None]): Function to call when clipboard changes.
                                             The function will receive the new clipboard
                                             content as a string parameter.
        
        Example:
            def on_clipboard_change(content):
                print(f"Clipboard changed: {content}")
            
            clipboard_manager.add_callback(on_clipboard_change)
        """
        self.callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[str], None]):
        """
        Remove a previously added callback function.
        
        Args:
            callback (Callable[[str], None]): The callback function to remove.
                                             Must be the same function object that
                                             was previously added.
        
        Example:
            clipboard_manager.remove_callback(on_clipboard_change)
        """
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def _notify_callbacks(self, new_content: str):
        """
        Notify all registered callbacks of a clipboard change.
        
        This method is called internally when new clipboard content is detected.
        It safely calls all registered callbacks, catching and logging any errors
        to prevent one callback from breaking others.
        
        Args:
            new_content (str): The new clipboard content to pass to callbacks.
        """
        for callback in self.callbacks:
            try:
                callback(new_content)
            except Exception as e:
                print(f"Error in clipboard callback: {e}")
    
    def start_monitoring(self):
        """
        Start monitoring clipboard changes in a background thread.
        
        This method starts the clipboard monitoring service. If monitoring is
        already active, it does nothing. The monitoring runs in a separate
        daemon thread to avoid blocking the main application.
        
        The monitoring thread will:
        1. Initialize with current clipboard content
        2. Continuously check for clipboard changes
        3. Update history when changes are detected
        4. Notify registered callbacks
        """
        if self.monitoring:
            return
        
        self.monitoring = True
        
        # Create a daemon thread for monitoring
        # Daemon threads automatically exit when the main program exits
        self.monitor_thread = threading.Thread(target=self._monitor_clipboard, daemon=True)
        self.monitor_thread.start()
        
        print("Clipboard monitoring started")
    
    def stop_monitoring(self):
        """
        Stop monitoring clipboard changes.
        
        This method gracefully stops the clipboard monitoring service.
        It sets the monitoring flag to False and waits for the monitoring
        thread to finish (with a timeout to prevent hanging).
        """
        self.monitoring = False
        
        if self.monitor_thread:
            # Wait for the monitoring thread to finish (max 1 second)
            self.monitor_thread.join(timeout=1)
        
        print("Clipboard monitoring stopped")
    
    def _monitor_clipboard(self):
        """
        Monitor clipboard for changes (runs in background thread).
        
        This is the main monitoring loop that runs in a separate thread.
        It continuously checks the clipboard for changes and updates the
        history when new content is detected.
        
        The monitoring loop:
        1. Initializes with current clipboard content
        2. Enters a continuous loop while monitoring is active
        3. Checks for clipboard changes at regular intervals
        4. Updates history and notifies callbacks when changes occur
        5. Handles errors gracefully to prevent crashes
        """
        # Initialize with current clipboard content
        try:
            self.current_clipboard = pyperclip.paste()
            # Add initial content to history if it's not empty
            if self.current_clipboard.strip():
                self._add_to_history(self.current_clipboard)
        except Exception as e:
            print(f"Error initializing clipboard: {e}")
        
        # Main monitoring loop
        while self.monitoring:
            try:
                # Get current clipboard content
                new_content = pyperclip.paste()
                
                # Check if clipboard content has changed
                if new_content != self.current_clipboard:
                    # Update our tracking
                    self.current_clipboard = new_content
                    
                    # Only process non-empty text content
                    if new_content and new_content.strip():
                        # Add to history
                        self._add_to_history(new_content)
                        
                        # Notify callbacks
                        self._notify_callbacks(new_content)
                
                # Sleep for the configured interval
                time.sleep(config.CLIPBOARD_MONITOR_INTERVAL)
                
            except Exception as e:
                print(f"Error monitoring clipboard: {e}")
                # Wait longer on error to prevent spam
                time.sleep(1)
    
    def _add_to_history(self, content: str):
        """
        Add content to clipboard history with duplicate handling.
        
        This method adds new content to the clipboard history while:
        1. Removing any existing duplicate entries
        2. Adding the new content to the front of the history
        3. Maintaining thread safety with locking
        
        Args:
            content (str): The clipboard content to add to history.
        """
        with self._lock:
            # Remove duplicate if it exists
            # We search through the deque and remove the duplicate
            # This ensures the most recent copy is at the front
            try:
                self.clipboard_history.remove(content)
            except ValueError:
                # Content not in history, which is fine
                pass
            
            # Add new content to the front of the history
            # deque.appendleft() adds to the front efficiently
            self.clipboard_history.appendleft(content)
    
    def get_clipboard_history(self) -> List[str]:
        """
        Get the current clipboard history as a list.
        
        Returns a copy of the current clipboard history with the most recent
        items first. This method is thread-safe and returns a snapshot of
        the current state.
        
        Returns:
            List[str]: List of clipboard history items, most recent first.
        
        Example:
            history = clipboard_manager.get_clipboard_history()
            print(f"Found {len(history)} clipboard items")
            for i, item in enumerate(history):
                print(f"{i+1}. {item[:50]}...")  # Show first 50 chars
        """
        with self._lock:
            # Convert deque to list for safe return
            return list(self.clipboard_history)
    
    def copy_to_clipboard(self, content: str):
        """
        Copy content to the system clipboard.
        
        This method updates the system clipboard with the provided content.
        It also updates our internal tracking to prevent the change from
        being processed as a new clipboard event.
        
        Args:
            content (str): The content to copy to the clipboard.
        
        Example:
            clipboard_manager.copy_to_clipboard("Hello, World!")
        """
        try:
            # Copy to system clipboard
            pyperclip.copy(content)
            
            # Update our internal tracking to prevent duplicate processing
            self.current_clipboard = content
            
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
    
    def get_current_clipboard(self) -> Optional[str]:
        """
        Get the current clipboard content directly from the system.
        
        This method bypasses the internal cache and directly queries the
        system clipboard. It's useful for getting the most up-to-date
        clipboard content.
        
        Returns:
            Optional[str]: Current clipboard content, or None if error occurs.
        
        Example:
            current = clipboard_manager.get_current_clipboard()
            if current:
                print(f"Current clipboard: {current}")
        """
        try:
            return pyperclip.paste()
        except Exception as e:
            print(f"Error getting clipboard content: {e}")
            return None
    
    def clear_history(self):
        """
        Clear the clipboard history.
        
        This method removes all items from the clipboard history.
        The current clipboard content is not affected, only the history
        is cleared. This operation is thread-safe.
        
        Example:
            clipboard_manager.clear_history()
            print("Clipboard history cleared")
        """
        with self._lock:
            self.clipboard_history.clear()
    
    def get_history_item(self, index: int) -> Optional[str]:
        """
        Get a specific item from clipboard history by index.
        
        This method retrieves a specific item from the clipboard history
        by its index position. Index 0 is the most recent item.
        
        Args:
            index (int): The index of the item to retrieve (0-based).
        
        Returns:
            Optional[str]: The clipboard item at the specified index,
                          or None if the index is out of range.
        
        Example:
            # Get the most recent item
            recent = clipboard_manager.get_history_item(0)
            
            # Get the third most recent item
            third = clipboard_manager.get_history_item(2)
        """
        with self._lock:
            if 0 <= index < len(self.clipboard_history):
                return self.clipboard_history[index]
            return None 