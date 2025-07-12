import keyboard
import threading
from typing import Dict, Callable, Optional
import traceback


class HotkeyManager:
    """Manages global keyboard shortcuts for SnapPad."""
    
    def __init__(self):
        self.hotkeys = {}
        self.monitoring = False
        self.monitor_thread = None
        self._lock = threading.Lock()
        print("HotkeyManager initialized")
    
    def register_hotkey(self, hotkey: str, callback: Callable, description: str = ""):
        """Register a global hotkey with a callback function."""
        with self._lock:
            if hotkey in self.hotkeys:
                print(f"Warning: Hotkey '{hotkey}' already registered. Overwriting.")
            
            self.hotkeys[hotkey] = {
                'callback': callback,
                'description': description
            }
            
            # If monitoring is already active, register the hotkey immediately
            if self.monitoring:
                try:
                    print(f"Attempting to register hotkey: {hotkey}")
                    keyboard.add_hotkey(hotkey, callback, suppress=True)
                    print(f"Successfully registered hotkey: {hotkey} - {description}")
                except Exception as e:
                    print(f"Error registering hotkey '{hotkey}': {e}")
                    print(traceback.format_exc())
    
    def unregister_hotkey(self, hotkey: str):
        """Unregister a global hotkey."""
        with self._lock:
            if hotkey in self.hotkeys:
                try:
                    keyboard.remove_hotkey(hotkey)
                    del self.hotkeys[hotkey]
                    print(f"Unregistered hotkey: {hotkey}")
                except Exception as e:
                    print(f"Error unregistering hotkey '{hotkey}': {e}")
                    print(traceback.format_exc())
    
    def start_monitoring(self):
        """Start monitoring for global hotkeys."""
        if self.monitoring:
            print("Hotkey monitoring already active")
            return
        
        self.monitoring = True
        print("Starting hotkey monitoring thread")
        self.monitor_thread = threading.Thread(target=self._monitor_hotkeys, daemon=True)
        self.monitor_thread.start()
        print("Hotkey monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring for global hotkeys."""
        self.monitoring = False
        
        # Remove all registered hotkeys
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
        """Monitor for hotkeys (runs in background thread)."""
        try:
            # Register all hotkeys
            with self._lock:
                print(f"Registering {len(self.hotkeys)} hotkeys")
                for hotkey, info in self.hotkeys.items():
                    try:
                        print(f"Attempting to register hotkey: {hotkey}")
                        keyboard.add_hotkey(hotkey, info['callback'], suppress=True)
                        print(f"Successfully registered hotkey: {hotkey} - {info['description']}")
                    except Exception as e:
                        print(f"Error registering hotkey '{hotkey}': {e}")
                        print(traceback.format_exc())
            
            # Keep the thread alive while monitoring
            print("Hotkey monitor thread running")
            while self.monitoring:
                try:
                    # keyboard.wait() would block forever, so we use sleep
                    threading.Event().wait(1)
                except KeyboardInterrupt:
                    print("KeyboardInterrupt received, stopping hotkey monitoring")
                    break
                
        except Exception as e:
            print(f"Error in hotkey monitoring: {e}")
            print(traceback.format_exc())
    
    def get_registered_hotkeys(self) -> Dict[str, str]:
        """Get all registered hotkeys and their descriptions."""
        with self._lock:
            return {hotkey: info['description'] for hotkey, info in self.hotkeys.items()}
    
    def is_monitoring(self) -> bool:
        """Check if hotkey monitoring is active."""
        return self.monitoring
    
    def test_hotkey(self, hotkey: str) -> bool:
        """Test if a hotkey combination is valid."""
        try:
            # Try to parse the hotkey
            keyboard.parse_hotkey(hotkey)
            print(f"Hotkey '{hotkey}' is valid")
            return True
        except ValueError as e:
            print(f"Hotkey '{hotkey}' is invalid: {e}")
            return False 