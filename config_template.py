# =============================================================================
# SNAP PAD CONFIGURATION TEMPLATE
# =============================================================================
# 
# Copy this file to config.py and fill in your settings
# This template file is safe to commit to version control
# 
# =============================================================================
# OPENAI API SETTINGS
# =============================================================================

# OpenAI API Key - Set this to your actual API key
# You can also set this as an environment variable: OPENAI_API_KEY
OPENAI_API_KEY = ""  # Leave empty to use environment variable

# OpenAI model to use for prompt enhancement
# Options: gpt-4, gpt-4-turbo, gpt-3.5-turbo, etc.
OPENAI_MODEL = "gpt-4"

# Maximum tokens for the enhanced prompt response
OPENAI_MAX_TOKENS = 1500

# Temperature for prompt generation (0.0 = deterministic, 1.0 = creative)
OPENAI_TEMPERATURE = 0.7

# System prompt for prompt enhancement
OPENAI_SYSTEM_PROMPT = """You are a prompt enhancement expert. Your job is to improve user prompts to make them more effective, clear, and detailed for AI models. 

When given a prompt, enhance it by:
1. Adding more context and specificity
2. Clarifying the desired output format
3. Including relevant constraints or requirements
4. Making it more actionable and clear
5. Preserving the original intent while improving structure

Return only the enhanced prompt, no explanations or additional text."""

# Whether to enable OpenAI features
OPENAI_ENABLED = True

# =============================================================================
# PROMPT ENHANCEMENT SETTINGS
# =============================================================================

# Maximum length of input prompt to process
PROMPT_MAX_INPUT_LENGTH = 3000

# Whether to automatically copy enhanced prompt to clipboard
AUTO_COPY_ENHANCED_PROMPT = True

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

# Global hotkey to enhance current clipboard content as a prompt
# This allows quick prompt enhancement without opening the dashboard
# The text currently in the clipboard will be enhanced using OpenAI
HOTKEY_ENHANCE_PROMPT = "ctrl+alt+e"

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

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_config():
    """Validate configuration settings and return any errors."""
    errors = []
    
    # Validate clipboard settings
    if not (1 <= CLIPBOARD_HISTORY_SIZE <= 50):
        errors.append("CLIPBOARD_HISTORY_SIZE must be between 1 and 50")
    
    if not (0.1 <= CLIPBOARD_MONITOR_INTERVAL <= 5.0):
        errors.append("CLIPBOARD_MONITOR_INTERVAL must be between 0.1 and 5.0 seconds")
    
    # Validate UI settings
    if not (100 <= REFRESH_INTERVAL <= 10000):
        errors.append("REFRESH_INTERVAL must be between 100 and 10000 milliseconds")
    
    if not (20 <= CLIPBOARD_DISPLAY_MAX_LENGTH <= 500):
        errors.append("CLIPBOARD_DISPLAY_MAX_LENGTH must be between 20 and 500 characters")
    
    return errors

def get_config_summary():
    """Return a summary of the current configuration."""
    return {
        'openai_enabled': OPENAI_ENABLED,
        'openai_model': OPENAI_MODEL,
        'clipboard_history_size': CLIPBOARD_HISTORY_SIZE,
        'dashboard_dimensions': f"{DASHBOARD_WIDTH}x{DASHBOARD_HEIGHT}",
        'hotkeys': {
            'toggle_dashboard': HOTKEY_TOGGLE_DASHBOARD,
            'save_note': HOTKEY_SAVE_NOTE,
            'enhance_prompt': HOTKEY_ENHANCE_PROMPT
        },
        'debug_mode': DEBUG_MODE
    } 