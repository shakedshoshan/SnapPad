"""
Configuration settings for SnapPad application.

This module contains all configurable settings for the SnapPad application.
Users can modify these values to customize the application behavior without
needing to modify the core application code.

The configuration is organized into logical sections:
- Clipboard Settings: Controls clipboard monitoring behavior
- Hotkey Settings: Defines global keyboard shortcuts
- Dashboard Settings: UI positioning and appearance
- Database Settings: Data storage configuration
- System Integration: Tray icon and auto-start options
- Debug Settings: Development and troubleshooting options

Author: SnapPad Team
Version: 1.0.0
"""

# =============================================================================
# CLIPBOARD SETTINGS
# =============================================================================

# Maximum number of clipboard items to store in memory
# This controls how many recent clipboard entries are kept in the history
# Range: 1-50 items (validated by validate_config())
CLIPBOARD_HISTORY_SIZE = 10

# Interval between clipboard checks in seconds
# Lower values make clipboard detection more responsive but use more CPU
# Higher values save CPU but may miss very quick clipboard changes
# Range: 0.1-5.0 seconds (validated by validate_config())
CLIPBOARD_MONITOR_INTERVAL = 0.5

# =============================================================================
# HOTKEY SETTINGS
# =============================================================================

# Global hotkey to toggle dashboard visibility
# Format: "modifier+modifier+key" (e.g., "ctrl+alt+s")
# Common modifiers: ctrl, alt, shift, win
# This hotkey will show/hide the dashboard from anywhere in the system
HOTKEY_TOGGLE_DASHBOARD = "ctrl+alt+s"

# Global hotkey to save current clipboard content as a note
# This allows quick saving of selected text without opening the dashboard
# The text currently in the clipboard will be saved as a new note
HOTKEY_SAVE_NOTE = "ctrl+alt+n"

# =============================================================================
# DASHBOARD SETTINGS
# =============================================================================

# Dashboard window dimensions in pixels
# The dashboard is designed to be compact and positioned on the right side
# Width: Space for clipboard items and notes (300-800 pixels)
DASHBOARD_WIDTH = 360

# Height: Enough space for clipboard history and notes (400-1200 pixels)
DASHBOARD_HEIGHT = 680

# Distance from the right edge of the screen in pixels
# This positions the dashboard as a side panel
DASHBOARD_POSITION_X_OFFSET = 10

# Whether to keep the dashboard always on top of other windows
# True: Dashboard stays visible above all other applications
# False: Dashboard can be hidden behind other windows
DASHBOARD_ALWAYS_ON_TOP = True

# =============================================================================
# DATABASE SETTINGS
# =============================================================================

# Folder name in %APPDATA% where the database will be stored
# Full path will be: %APPDATA%\SnapPad\snappad.db
DATABASE_FOLDER = "SnapPad"

# SQLite database filename
# This file will contain all persistent notes and application data
DATABASE_FILENAME = "snappad.db"

# =============================================================================
# UI SETTINGS
# =============================================================================

# How often to refresh the UI in milliseconds
# Lower values make the UI more responsive but use more CPU
# Higher values save CPU but may make the UI feel less responsive
# Range: 100-10000 milliseconds (validated by validate_config())
REFRESH_INTERVAL = 500

# Maximum length of clipboard text to display in the UI
# Longer text will be truncated with "..." for better readability
# Range: 20-500 characters (validated by validate_config())
CLIPBOARD_DISPLAY_MAX_LENGTH = 80

# Height of the text edit widget for editing notes in pixels
# This controls how much space is available when editing notes
NOTE_EDIT_HEIGHT = 60

# =============================================================================
# SYSTEM TRAY SETTINGS
# =============================================================================

# Whether to enable the system tray icon
# True: Application will minimize to system tray
# False: Application will use taskbar only
SYSTEM_TRAY_ENABLED = True

# Tooltip text shown when hovering over the system tray icon
# This helps users identify the application in the system tray
SYSTEM_TRAY_TOOLTIP = "SnapPad"

# =============================================================================
# AUTO-START SETTINGS (Future Implementation)
# =============================================================================

# Whether to automatically start with Windows
# Note: This feature is not yet implemented
AUTO_START_ENABLED = False

# Whether to start minimized to system tray
# Only relevant if AUTO_START_ENABLED is True
AUTO_START_MINIMIZED = True

# =============================================================================
# DEBUG SETTINGS
# =============================================================================

# Enable debug output and additional logging
# True: Print detailed information about application operations
# False: Only print essential information
DEBUG_MODE = True

# Whether to log to file instead of console
# Note: File logging is not yet implemented
LOG_TO_FILE = False

# =============================================================================
# THEME SETTINGS
# =============================================================================

# Color theme for the application
# These colors are used throughout the UI for consistency
# You can customize these values to change the application's appearance
THEME = {
    'background': '#ffffff',    # Main background color
    'foreground': '#000000',    # Main text color
    'accent': '#4CAF50',        # Accent color for buttons and highlights
    'danger': '#ff6b6b',        # Color for delete buttons and warnings
    'warning': '#ff9800',       # Color for warning messages
    'info': '#2196F3',          # Color for information messages
    'border': '#cccccc',        # Border color for UI elements
    'hover': '#e0e0e0'          # Hover color for interactive elements
}

# =============================================================================
# WINDOW BEHAVIOR SETTINGS
# =============================================================================

# Whether to hide the dashboard when it loses focus
# True: Dashboard automatically hides when clicking elsewhere
# False: Dashboard stays visible until manually hidden
HIDE_ON_FOCUS_LOSS = False

# Whether to minimize to system tray instead of taskbar
# True: Window minimizes to system tray
# False: Window minimizes to taskbar
MINIMIZE_TO_TRAY = True

# Whether to close to system tray instead of exiting
# True: Clicking X button minimizes to tray
# False: Clicking X button exits the application
CLOSE_TO_TRAY = True

# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================

def validate_config():
    """
    Validate all configuration values to ensure they're within acceptable ranges.
    
    This function checks each configuration value against its expected range
    and returns a list of any validation errors found. This helps prevent
    configuration mistakes that could cause application instability.
    
    Returns:
        list: List of validation error messages (empty if all values are valid)
    """
    errors = []
    
    # Validate clipboard history size
    if CLIPBOARD_HISTORY_SIZE < 1 or CLIPBOARD_HISTORY_SIZE > 50:
        errors.append("CLIPBOARD_HISTORY_SIZE must be between 1 and 50")
    
    # Validate clipboard monitor interval
    if CLIPBOARD_MONITOR_INTERVAL < 0.1 or CLIPBOARD_MONITOR_INTERVAL > 5.0:
        errors.append("CLIPBOARD_MONITOR_INTERVAL must be between 0.1 and 5.0")
    
    # Validate dashboard dimensions
    if DASHBOARD_WIDTH < 300 or DASHBOARD_WIDTH > 800:
        errors.append("DASHBOARD_WIDTH must be between 300 and 800")
    
    if DASHBOARD_HEIGHT < 400 or DASHBOARD_HEIGHT > 1200:
        errors.append("DASHBOARD_HEIGHT must be between 400 and 1200")
    
    # Validate UI refresh interval
    if REFRESH_INTERVAL < 100 or REFRESH_INTERVAL > 10000:
        errors.append("REFRESH_INTERVAL must be between 100 and 10000")
    
    # Validate clipboard display length
    if CLIPBOARD_DISPLAY_MAX_LENGTH < 20 or CLIPBOARD_DISPLAY_MAX_LENGTH > 500:
        errors.append("CLIPBOARD_DISPLAY_MAX_LENGTH must be between 20 and 500")
    
    return errors

def get_config_summary():
    """
    Generate a human-readable summary of the current configuration.
    
    This function creates a formatted string containing the most important
    configuration settings. It's useful for debugging and for users who
    want to verify their current settings.
    
    Returns:
        str: Formatted configuration summary
    """
    return f"""
Current Configuration:
- Clipboard History Size: {CLIPBOARD_HISTORY_SIZE}
- Toggle Dashboard Hotkey: {HOTKEY_TOGGLE_DASHBOARD}
- Save Note Hotkey: {HOTKEY_SAVE_NOTE}
- Dashboard Size: {DASHBOARD_WIDTH}x{DASHBOARD_HEIGHT}
- System Tray: {'Enabled' if SYSTEM_TRAY_ENABLED else 'Disabled'}
- Debug Mode: {'Enabled' if DEBUG_MODE else 'Disabled'}
    """

# =============================================================================
# CONFIGURATION VALIDATION ON IMPORT
# =============================================================================

# Automatically validate configuration when this module is imported
# This ensures configuration errors are caught early during application startup
_config_errors = validate_config()
if _config_errors:
    print("Configuration Errors:")
    for error in _config_errors:
        print(f"  - {error}")
    print("Please fix these errors in config.py")
    
# Show debug information if debug mode is enabled
if DEBUG_MODE:
    print("Debug mode enabled")
    print(get_config_summary()) 