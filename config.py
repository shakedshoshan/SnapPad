"""
Configuration settings for SnapPad application.
Modify these values to customize the application behavior.
"""

# Clipboard Settings
CLIPBOARD_HISTORY_SIZE = 10  # Number of clipboard items to remember
CLIPBOARD_MONITOR_INTERVAL = 0.5  # Seconds between clipboard checks

# Hotkey Settings
HOTKEY_TOGGLE_DASHBOARD = "ctrl+alt+s"  # Show/hide dashboard
HOTKEY_SAVE_NOTE = "ctrl+alt+n"  # Save selected text as note

# Dashboard Settings
DASHBOARD_WIDTH = 360  # Reduced from 380 for more compact design
DASHBOARD_HEIGHT = 580  # Reduced from 600 for more compact design
DASHBOARD_POSITION_X_OFFSET = 10  # Distance from right edge of screen
DASHBOARD_ALWAYS_ON_TOP = True  # Keep dashboard always on top

# Database Settings
DATABASE_FOLDER = "SnapPad"  # Folder name in %APPDATA%
DATABASE_FILENAME = "snappad.db"  # SQLite database filename

# UI Settings
REFRESH_INTERVAL = 500  # Reduced from 1000ms for more responsive UI
CLIPBOARD_DISPLAY_MAX_LENGTH = 80  # Reduced from 100 for compact display
NOTE_EDIT_HEIGHT = 60  # Reduced from 80 for compact design

# System Tray Settings
SYSTEM_TRAY_ENABLED = True  # Enable system tray icon
SYSTEM_TRAY_TOOLTIP = "SnapPad"

# Auto-start Settings (for future implementation)
AUTO_START_ENABLED = False  # Auto-start with Windows
AUTO_START_MINIMIZED = True  # Start minimized to system tray

# Debug Settings
DEBUG_MODE = True  # Enable debug output
LOG_TO_FILE = False  # Log to file instead of console

# Color Theme Settings
THEME = {
    'background': '#ffffff',
    'foreground': '#000000',
    'accent': '#4CAF50',
    'danger': '#ff6b6b',
    'warning': '#ff9800',
    'info': '#2196F3',
    'border': '#cccccc',
    'hover': '#e0e0e0'
}

# Window Behavior
HIDE_ON_FOCUS_LOSS = False  # Hide dashboard when it loses focus
MINIMIZE_TO_TRAY = True  # Minimize to system tray instead of taskbar
CLOSE_TO_TRAY = True  # Close to system tray instead of exiting

# Validation functions
def validate_config():
    """Validate configuration values."""
    errors = []
    
    if CLIPBOARD_HISTORY_SIZE < 1 or CLIPBOARD_HISTORY_SIZE > 50:
        errors.append("CLIPBOARD_HISTORY_SIZE must be between 1 and 50")
    
    if CLIPBOARD_MONITOR_INTERVAL < 0.1 or CLIPBOARD_MONITOR_INTERVAL > 5.0:
        errors.append("CLIPBOARD_MONITOR_INTERVAL must be between 0.1 and 5.0")
    
    if DASHBOARD_WIDTH < 300 or DASHBOARD_WIDTH > 800:
        errors.append("DASHBOARD_WIDTH must be between 300 and 800")
    
    if DASHBOARD_HEIGHT < 400 or DASHBOARD_HEIGHT > 1200:
        errors.append("DASHBOARD_HEIGHT must be between 400 and 1200")
    
    if REFRESH_INTERVAL < 100 or REFRESH_INTERVAL > 10000:
        errors.append("REFRESH_INTERVAL must be between 100 and 10000")
    
    if CLIPBOARD_DISPLAY_MAX_LENGTH < 20 or CLIPBOARD_DISPLAY_MAX_LENGTH > 500:
        errors.append("CLIPBOARD_DISPLAY_MAX_LENGTH must be between 20 and 500")
    
    return errors

def get_config_summary():
    """Get a summary of current configuration."""
    return f"""
Current Configuration:
- Clipboard History Size: {CLIPBOARD_HISTORY_SIZE}
- Toggle Dashboard Hotkey: {HOTKEY_TOGGLE_DASHBOARD}
- Save Note Hotkey: {HOTKEY_SAVE_NOTE}
- Dashboard Size: {DASHBOARD_WIDTH}x{DASHBOARD_HEIGHT}
- System Tray: {'Enabled' if SYSTEM_TRAY_ENABLED else 'Disabled'}
- Debug Mode: {'Enabled' if DEBUG_MODE else 'Disabled'}
    """

# Validate configuration on import
_config_errors = validate_config()
if _config_errors:
    print("Configuration Errors:")
    for error in _config_errors:
        print(f"  - {error}")
    print("Please fix these errors in config.py")
    
if DEBUG_MODE:
    print("Debug mode enabled")
    print(get_config_summary()) 