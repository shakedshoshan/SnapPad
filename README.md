# SnapPad 📋

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green.svg)](https://pypi.org/project/PyQt6/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/en-us/windows)

A lightweight, always-on-top Windows application for managing clipboard history and persistent notes with global hotkeys.

## ✨ Features

- **🚀 Background Service**: Runs silently with minimal resource usage
- **⌨️ Global Hotkeys**: Customizable keyboard shortcuts for instant access
- **📋 Clipboard History**: Automatically tracks and stores your last 10 copied items
- **📝 Notes Management**: Persistent SQLite database for your personal notes
- **🖥️ Side Dashboard**: Modern, always-on-top interface positioned on the right side
- **🔧 System Tray**: Minimizes to system tray for easy access and management
- **⚙️ Configurable**: Easy-to-modify configuration for all settings

## 🚀 Quick Start

### Method 1: Docker (Recommended for Cross-Platform)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/snappad.git
cd snappad

# 2. Run with Docker (Linux/macOS)
./run-docker.sh start

# 2. Run with Docker (Windows)
run-docker.bat start
```

### Method 2: Native Installation

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/snappad.git
cd snappad

# 2. Run the installer
double-click install.bat
```

### Method 3: Manual Installation

```bash
# 1. Install Python 3.7+ from https://python.org
# 2. Install dependencies
pip install -r requirements.txt  # Use requirements-docker.txt for Linux/macOS

# 3. Run the application
python main.py
```

## 🎮 Usage

### Starting the Application

- **Quick Start**: Double-click `install.bat` (handles installation and startup)
- **Command Line**: `python main.py`
- **System Tray**: Look for the SnapPad icon in your system tray

### Default Hotkeys

| Hotkey | Action |
|--------|--------|
| `Ctrl + Alt + S` | Toggle dashboard visibility |
| `Ctrl + Alt + N` | Save current clipboard as note |

### Dashboard Features

#### 📋 Clipboard History
- Automatically captures all copied text
- Click any item to copy it back to clipboard
- Shows your last 10 unique items
- Removes duplicates automatically

#### 📝 My Notes
- Add notes directly in the dashboard
- Edit existing notes with the "Edit" button
- Delete notes with confirmation dialog
- All notes are permanently saved to SQLite database

### System Tray Options

Right-click the tray icon for:
- **Show/Hide Dashboard**
- **Clear Clipboard History**
- **About Information**
- **Exit Application**

Double-click the tray icon to toggle dashboard visibility.

## ⚙️ Configuration

Customize your experience by editing `config.py`:

```python
# Clipboard Settings
CLIPBOARD_HISTORY_SIZE = 10  # Number of items to remember
CLIPBOARD_MONITOR_INTERVAL = 0.5  # Check interval in seconds

# Hotkey Settings
HOTKEY_TOGGLE_DASHBOARD = "ctrl+alt+s"  # Show/hide dashboard
HOTKEY_SAVE_NOTE = "ctrl+alt+n"  # Save clipboard as note

# Dashboard Settings
DASHBOARD_WIDTH = 360  # Window width
DASHBOARD_HEIGHT = 580  # Window height
DASHBOARD_ALWAYS_ON_TOP = True  # Keep on top of other windows

# UI Settings
REFRESH_INTERVAL = 500  # UI refresh rate in milliseconds
```

## 💾 Data Storage

Your data is stored securely in:
- **Location**: `%APPDATA%\SnapPad\snappad.db`
- **Format**: SQLite database
- **Notes**: Stored permanently with timestamps
- **Clipboard History**: Stored in memory (resets on restart)

## 🔧 Auto-Start Setup

To run SnapPad automatically when Windows starts:

1. Create a shortcut to `install.bat`
2. Open Windows Startup folder:
   - Press `Win + R`
   - Type `shell:startup`
   - Press Enter
3. Copy the shortcut to this folder
4. Restart your computer to test

Note: The `install.bat` file will automatically detect if SnapPad is already installed and just start the application.

## 🧪 Testing

To test if SnapPad is working correctly:

1. Run the application: `python main.py`
2. Check the system tray for the SnapPad icon
3. Test hotkeys: `Ctrl+Alt+S` (toggle dashboard), `Ctrl+Alt+N` (save note)
4. Copy some text and verify it appears in the clipboard history
5. Add a note and verify it's saved between sessions

## 🛠️ Troubleshooting

### Common Issues

<details>
<summary><strong>🐍 "Python is not installed"</strong></summary>

**Solution:**
1. Download Python from [python.org](https://python.org)
2. ✅ **Important**: Check "Add Python to PATH" during installation
3. Restart your command prompt/terminal
</details>

<details>
<summary><strong>📦 "Failed to install dependencies"</strong></summary>

**Solution:**
```bash
# Update pip first
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# If still failing, try:
pip install PyQt6 pyperclip keyboard pywin32
```
</details>

<details>
<summary><strong>⌨️ "Hotkeys not working"</strong></summary>

**Solution:**
1. Check if another application is using the same hotkeys
2. Try different key combinations in `config.py`
3. Run the application as administrator
4. Verify hotkeys with: `python test_application.py`
</details>

<details>
<summary><strong>🖥️ "Dashboard not showing"</strong></summary>

**Solution:**
1. Press `Ctrl + Alt + S` to toggle visibility
2. Check system tray and double-click the icon
3. Verify the application is running in Task Manager
4. Check for error messages in the console
</details>

## 🐳 Docker Support

SnapPad now includes full Docker support for easy deployment and cross-platform compatibility!

### Docker Features
- **🖥️ Full GUI Support**: Complete PyQt6 interface with X11 forwarding
- **📋 Clipboard Integration**: Cross-platform clipboard access
- **⌨️ Global Hotkeys**: System-wide keyboard shortcuts
- **💾 Persistent Data**: Your notes and settings are preserved
- **🔄 Auto-restart**: Container restarts automatically on failure
- **🛡️ Security**: Runs as non-root user with proper isolation

### Quick Docker Start
```bash
# Linux/macOS
./run-docker.sh start

# Windows
run-docker.bat start
```

📖 **Full Docker Documentation**: See [DOCKER.md](DOCKER.md) for complete setup instructions, troubleshooting, and advanced configuration.

## 📁 Project Structure

```
SnapPad/
├── 📄 main.py                 # Application entry point
├── ⚙️ config.py              # Configuration settings
├── 🗄️ database.py            # SQLite database operations
├── 📋 clipboard_manager.py   # Clipboard monitoring & history
├── ⌨️ hotkey_manager.py      # Global hotkey management
├── 🖥️ dashboard.py           # PyQt6 user interface
├── 📦 requirements.txt       # Python dependencies (Windows/native)
├── 📦 requirements-docker.txt # Docker dependencies (Linux/macOS)
├── 🚀 install.bat            # Native installation & launcher
├── 🐳 Dockerfile            # Docker image configuration
├── 🐳 docker-compose.yml    # Docker Compose configuration
├── 🐳 run-docker.sh         # Docker runner script (Linux/macOS)
├── 🐳 run-docker.bat        # Docker runner script (Windows)
├── 📖 README.md             # This documentation
└── 📖 DOCKER.md             # Docker setup guide
```

## 🔧 Technical Stack

- **Language**: Python 3.7+
- **GUI Framework**: PyQt6
- **Database**: SQLite
- **Clipboard**: pyperclip
- **Hotkeys**: keyboard library
- **Platform**: Windows 10/11

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Bug Reports & Feature Requests

Found a bug or have a feature request? Please [open an issue](https://github.com/yourusername/snappad/issues) with:
- **Bug Reports**: Steps to reproduce, expected vs actual behavior
- **Feature Requests**: Detailed description of the proposed feature

## 🎯 Future Enhancements

- [ ] Rich text notes support
- [ ] Note categories and tags
- [ ] Search functionality across notes
- [ ] Cloud synchronization
- [ ] Custom themes and dark mode
- [ ] File attachment support
- [ ] Multi-language support
- [ ] Cross-platform compatibility

## 📊 Screenshots

> 🖼️ **Coming Soon**: Screenshots of the dashboard and system tray integration

---

<div align="center">
<strong>Made with ❤️ for productivity enthusiasts</strong>
</div> 