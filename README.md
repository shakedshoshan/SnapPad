# QuickSave & Notes - MVP

A lightweight Windows application for quick clipboard history and persistent notes management.

## Features

- **Background Service**: Runs silently in the background with minimal resource usage
- **Global Hotkeys**: Customizable keyboard shortcuts for quick access
- **Clipboard History**: Automatically tracks last 10 copied text snippets
- **Notes Management**: Persistent SQLite database storage for personal notes
- **Side Dashboard**: Always-on-top right-side interface with modern UI
- **System Tray**: Minimizes to system tray for easy access
- **Configurable**: Easy-to-modify configuration file

## Quick Start

### Method 1: Automatic Setup (Recommended)
1. **Download** all files to a folder
2. **Double-click** `install_and_run.bat`
3. **Follow** the setup prompts
4. **Done!** The application will be running

### Method 2: Manual Installation
1. **Install Python 3.x** from https://python.org (make sure to check "Add to PATH")
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Run the application**:
   ```bash
   python main.py
   ```

### Method 3: Quick Launch
- **Double-click** `start_quicksave.bat` (installs dependencies if needed)

## Usage

### Starting the Application
- **Double-click** `start_quicksave.bat`, or
- **Run** `python main.py` from command line
- **Check** system tray for the application icon

### Global Shortcuts (Default)
- **`Ctrl + Alt + S`**: Toggle dashboard visibility
- **`Ctrl + Alt + N`**: Save current clipboard content as a note

### Dashboard Features
- **Clipboard History**: 
  - Automatically captures copied text
  - Click any item to copy it back to clipboard
  - Shows last 10 unique items
- **My Notes**: 
  - Add notes directly in the dashboard
  - Edit notes by clicking the "Edit" button
  - Delete notes with confirmation
  - All notes are saved permanently

### System Tray
- **Right-click** the tray icon for options:
  - Show/Hide Dashboard
  - Clear Clipboard History
  - About Information
  - Exit Application
- **Double-click** the tray icon to toggle dashboard

## Configuration

Edit `config.py` to customize:
- **Hotkeys**: Change keyboard shortcuts
- **Dashboard Size**: Adjust window dimensions
- **Clipboard History**: Change number of items stored
- **UI Refresh Rate**: Adjust performance settings
- **Colors and Themes**: Customize appearance

## Data Storage

Application data is stored in: `%APPDATA%\QuickSaveNotes\quicksavenotes.db`

- **Notes**: Stored permanently in SQLite database
- **Clipboard History**: Stored in memory (resets on restart)
- **Settings**: Configurable via `config.py`

## Auto-Start Setup

To run automatically on Windows startup:
1. **Create** a shortcut to `start_quicksave.bat`
2. **Open** Windows Startup folder:
   - Press `Win + R`, type `shell:startup`, press Enter
3. **Copy** the shortcut to this folder
4. **Restart** your computer to test

## Testing

Run the test suite to verify everything works:
```bash
python test_application.py
```

## Troubleshooting

### Common Issues

1. **"Python is not installed"**
   - Download Python from https://python.org
   - Make sure to check "Add Python to PATH" during installation

2. **"Failed to install dependencies"**
   - Check your internet connection
   - Try running: `pip install --upgrade pip`
   - Then run: `pip install -r requirements.txt`

3. **Hotkeys not working**
   - Make sure no other application is using the same hotkeys
   - Try different key combinations in `config.py`
   - Run as administrator if needed

4. **Dashboard not showing**
   - Press the hotkey (`Ctrl + Alt + S`) to toggle
   - Check system tray and double-click the icon
   - Make sure the application is running

### Getting Help

- **Check** the system tray for the application icon
- **Look** for error messages in the command prompt
- **Run** `python test_application.py` to test components
- **Restart** the application if issues persist

## Project Structure

```
SnapPad/
├── main.py                 # Main application entry point
├── config.py              # Configuration settings
├── database.py            # SQLite database operations
├── clipboard_manager.py   # Clipboard monitoring
├── hotkey_manager.py      # Global hotkey handling
├── dashboard.py           # PyQt6 user interface
├── test_application.py    # Test suite
├── requirements.txt       # Python dependencies
├── install_and_run.bat    # Automatic installer
├── start_quicksave.bat    # Quick launcher
└── README.md             # This file
```

## Technical Details

- **Language**: Python 3.x
- **GUI Framework**: PyQt6
- **Database**: SQLite
- **Clipboard**: pyperclip
- **Hotkeys**: keyboard library
- **Platform**: Windows (tested on Windows 10/11)

## Future Enhancements

The current MVP includes all core features. Future versions might include:
- Rich text notes
- Note categories and tags
- Search functionality
- Cloud synchronization
- Custom themes
- File attachment support 