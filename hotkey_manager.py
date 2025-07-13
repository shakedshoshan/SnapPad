"""
Hotkey Manager for SnapPad

This module handles global keyboard shortcuts (hotkeys) for the SnapPad application.
It provides system-wide hotkey registration, monitoring, and management capabilities
that work regardless of which application currently has focus.

Key Features:
- Global hotkey registration using the keyboard library
- Thread-safe hotkey management with proper locking
- Background monitoring thread for hotkey detection
- Validation of hotkey combinations before registration
- Graceful error handling and recovery
- Dynamic hotkey registration and unregistration
- Callback system for hotkey activation

The hotkey manager uses the keyboard library for low-level keyboard hook
registration and provides a clean interface for the rest of the application.

Author: SnapPad Team
Version: 1.0.0
"""

import keyboard
import threading
from typing import Dict, Callable, Optional
import traceback


class HotkeyManager:
    """
    Manages global keyboard shortcuts for SnapPad.
    
    This class provides comprehensive hotkey management including:
    - Registration of global hotkeys with callback functions
    - Background monitoring thread for hotkey detection
    - Thread-safe operations with proper locking
    - Validation of hotkey combinations
    - Error handling and recovery
    - Dynamic hotkey management (add/remove during runtime)
    
    The manager uses the keyboard library's global hook functionality
    to capture hotkey events system-wide, regardless of which application
    currently has focus.
    
    Thread Safety:
    All hotkey operations are thread-safe using threading.Lock() to prevent
    race conditions between the monitoring thread and main application thread.
    """
    
    def __init__(self):
        """
        Initialize the hotkey manager.
        
        This constructor sets up the internal data structures and prepares
        the manager for hotkey registration and monitoring. The monitoring
        thread is not started until start_monitoring() is called.
        """
        # Dictionary to store registered hotkeys and their callbacks
        # Format: {'hotkey_string': {'callback': function, 'description': string}}
        self.hotkeys = {}
        
        # Monitoring state
        self.monitoring = False
        self.monitor_thread = None
        
        # Thread safety lock
        self._lock = threading.Lock()
        
        print("HotkeyManager initialized")
    
    def register_hotkey(self, hotkey: str, callback: Callable, description: str = ""):
        """
        Register a global hotkey with a callback function.
        
        This method registers a hotkey combination that will trigger the
        provided callback function when pressed. The hotkey works globally,
        meaning it will trigger regardless of which application has focus.
        
        Args:
            hotkey (str): The hotkey combination (e.g., "ctrl+alt+s").
                         Common modifiers: ctrl, alt, shift, win
                         Example formats: "ctrl+s", "alt+f4", "ctrl+alt+del"
            callback (Callable): The function to call when the hotkey is pressed.
                               Should be a thread-safe function as it may be called
                               from the monitoring thread.
            description (str): Optional description of what the hotkey does.
                             Used for logging and debugging.
        
        Example:
            def toggle_window():
                print("Hotkey pressed!")
            
            manager.register_hotkey("ctrl+alt+s", toggle_window, "Toggle window")
        """
        with self._lock:
            # Check if hotkey is already registered
            if hotkey in self.hotkeys:
                print(f"Warning: Hotkey '{hotkey}' already registered. Overwriting.")
            
            # Store the hotkey information
            self.hotkeys[hotkey] = {
                'callback': callback,
                'description': description
            }
            
            # If monitoring is already active, register the hotkey immediately
            if self.monitoring:
                try:
                    print(f"Attempting to register hotkey: {hotkey}")
                    
                    # Register the hotkey with the keyboard library
                    # suppress=True prevents the hotkey from being passed to other applications
                    keyboard.add_hotkey(hotkey, callback, suppress=True)
                    
                    print(f"Successfully registered hotkey: {hotkey} - {description}")
                    
                except Exception as e:
                    print(f"Error registering hotkey '{hotkey}': {e}")
                    print(traceback.format_exc())
    
    def unregister_hotkey(self, hotkey: str):
        """
        Unregister a previously registered global hotkey.
        
        This method removes a hotkey from both the internal registry and
        the system-level keyboard hook. After unregistration, the hotkey
        will no longer trigger its callback function.
        
        Args:
            hotkey (str): The hotkey combination to unregister.
                         Must exactly match the string used during registration.
        
        Example:
            manager.unregister_hotkey("ctrl+alt+s")
        """
        with self._lock:
            if hotkey in self.hotkeys:
                try:
                    # Remove from system keyboard hook
                    keyboard.remove_hotkey(hotkey)
                    
                    # Remove from internal registry
                    del self.hotkeys[hotkey]
                    
                    print(f"Unregistered hotkey: {hotkey}")
                    
                except Exception as e:
                    print(f"Error unregistering hotkey '{hotkey}': {e}")
                    print(traceback.format_exc())
    
    def start_monitoring(self):
        """
        Start monitoring for global hotkeys in a background thread.
        
        This method starts the hotkey monitoring service. If monitoring is
        already active, it does nothing. The monitoring runs in a separate
        daemon thread to avoid blocking the main application.
        
        The monitoring thread will:
        1. Register all currently stored hotkeys with the system
        2. Keep the thread alive to maintain hotkey functionality
        3. Handle any errors that occur during monitoring
        """
        if self.monitoring:
            print("Hotkey monitoring already active")
            return
        
        self.monitoring = True
        
        print("Starting hotkey monitoring thread")
        
        # Create a daemon thread for monitoring
        # Daemon threads automatically exit when the main program exits
        self.monitor_thread = threading.Thread(target=self._monitor_hotkeys, daemon=True)
        self.monitor_thread.start()
        
        print("Hotkey monitoring started")
    
    def stop_monitoring(self):
        """
        Stop monitoring for global hotkeys.
        
        This method gracefully stops the hotkey monitoring service.
        It removes all registered hotkeys from the system and stops
        the monitoring thread.
        """
        self.monitoring = False
        
        # Remove all registered hotkeys from the system
        with self._lock:
            print("Removing all registered hotkeys")
            for hotkey in list(self.hotkeys.keys()):
                try:
                    keyboard.remove_hotkey(hotkey)
                    print(f"Removed hotkey: {hotkey}")
                except Exception as e:
                    print(f"Error removing hotkey '{hotkey}': {e}")
                    print(traceback.format_exc())
        
        print("Hotkey monitoring stopped")
    
    def _monitor_hotkeys(self):
        """
        Monitor for hotkeys in the background thread.
        
        This is the main monitoring loop that runs in a separate thread.
        It registers all stored hotkeys with the system and keeps the
        thread alive to maintain hotkey functionality.
        
        The monitoring loop:
        1. Registers all stored hotkeys with the keyboard library
        2. Enters a keep-alive loop while monitoring is active
        3. Handles any errors that occur during monitoring
        4. Provides graceful shutdown when monitoring stops
        """
        try:
            # Register all stored hotkeys with the system
            with self._lock:
                print(f"Registering {len(self.hotkeys)} hotkeys")
                for hotkey, info in self.hotkeys.items():
                    try:
                        print(f"Attempting to register hotkey: {hotkey}")
                        
                        # Register the hotkey with the keyboard library
                        # suppress=True prevents the hotkey from being passed to other applications
                        keyboard.add_hotkey(hotkey, info['callback'], suppress=True)
                        
                        print(f"Successfully registered hotkey: {hotkey} - {info['description']}")
                        
                    except Exception as e:
                        print(f"Error registering hotkey '{hotkey}': {e}")
                        print(traceback.format_exc())
            
            # Keep the thread alive while monitoring is active
            print("Hotkey monitor thread running")
            while self.monitoring:
                try:
                    # Use threading.Event().wait() instead of keyboard.wait()
                    # to allow for graceful shutdown
                    threading.Event().wait(1)
                    
                except KeyboardInterrupt:
                    print("KeyboardInterrupt received, stopping hotkey monitoring")
                    break
                
        except Exception as e:
            print(f"Error in hotkey monitoring: {e}")
            print(traceback.format_exc())
    
    def get_registered_hotkeys(self) -> Dict[str, str]:
        """
        Get all registered hotkeys and their descriptions.
        
        This method returns a dictionary mapping hotkey combinations to
        their descriptions. It's useful for debugging and for displaying
        current hotkey bindings to users.
        
        Returns:
            Dict[str, str]: Dictionary mapping hotkey strings to descriptions.
        
        Example:
            hotkeys = manager.get_registered_hotkeys()
            print("Registered hotkeys:")
            for hotkey, description in hotkeys.items():
                print(f"  {hotkey}: {description}")
        """
        with self._lock:
            return {hotkey: info['description'] for hotkey, info in self.hotkeys.items()}
    
    def is_monitoring(self) -> bool:
        """
        Check if hotkey monitoring is currently active.
        
        Returns:
            bool: True if monitoring is active, False otherwise.
        
        Example:
            if manager.is_monitoring():
                print("Hotkeys are being monitored")
            else:
                print("Hotkey monitoring is not active")
        """
        return self.monitoring
    
    def test_hotkey(self, hotkey: str) -> bool:
        """
        Test if a hotkey combination is valid without registering it.
        
        This method validates a hotkey string by attempting to parse it
        with the keyboard library. It's useful for validating user input
        before attempting to register hotkeys.
        
        Args:
            hotkey (str): The hotkey combination to validate.
        
        Returns:
            bool: True if the hotkey is valid, False otherwise.
        
        Example:
            if manager.test_hotkey("ctrl+alt+s"):
                print("Hotkey is valid")
            else:
                print("Invalid hotkey format")
        """
        try:
            # Try to parse the hotkey combination
            keyboard.parse_hotkey(hotkey)
            print(f"Hotkey '{hotkey}' is valid")
            return True
            
        except ValueError as e:
            print(f"Hotkey '{hotkey}' is invalid: {e}")
            return False 