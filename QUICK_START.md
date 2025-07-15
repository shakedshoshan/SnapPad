# SnapPad - Quick Start Guide

## Installation & First Run

**Recommended:** Double-click **`install.bat`** for automatic setup:

- **`install.bat`** - Handles everything: Python check, dependency installation, and optional startup

The install script will:
1. ✓ Check if Python is installed
2. ✓ Update pip to latest version  
3. ✓ Install all required packages (PyQt6, pyperclip, keyboard, pywin32)
4. ✓ Test the installation
5. ✓ Optionally start SnapPad

## Manual Installation

If you prefer manual setup:
1. Make sure Python 3.7+ is installed
2. Run: `pip install -r requirements.txt`
3. Run: `python main.py`

## How to Run SnapPad

After installation, you can start SnapPad by:

- **Double-click `install.bat`** (works as both installer and launcher)
- **Double-click `SnapPad.bat`** (simple launcher with detailed output)
- **OR run:** `python main.py`

### Launcher Files Explained:
- **`install.bat`** - Full setup script + launcher (recommended for first run)
- **`SnapPad.bat`** - Simple launcher with helpful status messages

## What You'll See

1. A console window will open (keep it open!)
2. The SnapPad dashboard will appear on the right side of your screen
3. The app will start monitoring your clipboard automatically
4. Look for the SnapPad icon in your system tray

## How to Use

- **Ctrl+Alt+S** - Show/hide the dashboard
- **Ctrl+Alt+N** - Save current clipboard as a note
- **Right-click system tray icon** - Access menu options

## Files in This Folder

### Launcher Files:
- **`install.bat`** - **← Click this first for installation and setup**
- **`SnapPad.bat`** - Simple launcher with detailed status messages  

### Core Files:
- `main.py` - Main application entry point
- `requirements.txt` - Python dependencies
- Other `.py` files - Source code modules

## Notes

- Keep the console window open while using SnapPad
- Your notes are saved automatically to `%APPDATA%\SnapPad\`
- You can minimize the console window, but don't close it
- The application runs from Python source code (no compilation needed)

## Troubleshooting

If SnapPad doesn't start:
1. **Run `install.bat` as administrator** if installation fails
2. Make sure Python 3.7+ is installed and in your PATH
3. Check your internet connection for dependency downloads
4. If you see import errors, re-run `install.bat` to reinstall dependencies

---
**Enjoy using SnapPad! 📋** 