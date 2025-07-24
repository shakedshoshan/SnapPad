# SnapPad 📋

[![Python](https://img.shields.io/badge/python-3.7%2B-blue.svg)](https://www.python.org/downloads/)
[![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green.svg)](https://pypi.org/project/PyQt6/)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/en-us/windows)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](LICENSE)

> A powerful, lightweight Windows clipboard manager and note-taking application with AI-powered features, designed for developers, writers, and productivity enthusiasts.

## 🎯 Project Purpose

SnapPad solves the common productivity challenges of losing clipboard content and managing quick notes efficiently. It's a comprehensive solution that combines clipboard history management, persistent note-taking, and AI-powered features to enhance your workflow.

### Core Problems Solved:
- **Lost Clipboard Content**: Never lose important copied text again with automatic clipboard history tracking
- **Scattered Notes**: Centralized, persistent note storage with SQLite database
- **Poor AI Prompts**: AI-powered prompt enhancement for better AI interactions
- **Context Switching**: Global hotkeys for instant access without interrupting your workflow
- **Productivity Loss**: Streamlined interface that stays out of your way until needed

## 🏗️ Technical Architecture

### Core Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **GUI Framework** | PyQt6 (Qt6) | Modern, cross-platform UI with native Windows integration |
| **Database** | SQLite | Lightweight, file-based persistent storage |
| **Clipboard Access** | pyperclip | Cross-platform clipboard monitoring |
| **Global Hotkeys** | keyboard library | System-wide keyboard shortcut registration |
| **AI Integration** | OpenAI API | GPT-powered prompt enhancement and smart responses |
| **Windows Integration** | pywin32 | System tray, Windows APIs, background services |
| **Threading** | Python threading | Background services and UI responsiveness |

### System Requirements
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.7 or higher
- **RAM**: Minimum 50MB, typical usage ~10-20MB
- **Storage**: ~5MB application + database size
- **Network**: Internet connection for AI features (optional)

## ✨ Key Features

### 📋 Smart Clipboard Management
- **Automatic Tracking**: Monitors clipboard changes every 500ms (configurable)
- **History Storage**: Maintains last 15 unique clipboard items (configurable)
- **Duplicate Prevention**: Automatically removes duplicate entries
- **Instant Access**: Click any item to copy back to clipboard
- **Background Operation**: Runs silently without interfering with other applications

### 📝 Persistent Notes System
- **SQLite Database**: All notes stored in `%APPDATA%\SnapPad\snappad.db`
- **CRUD Operations**: Create, read, update, delete notes with full persistence
- **Inline Editing**: Edit notes directly in the interface
- **Priority System**: Organize notes by importance (1-5 scale)
- **Search & Filter**: Find notes quickly with built-in search functionality
- **Auto-save**: Changes saved automatically to prevent data loss

### 🤖 AI-Powered Features

#### Prompt Enhancement
- **OpenAI Integration**: Uses GPT-3.5-turbo/GPT-4 for intelligent prompt improvement
- **Smart Enhancement**: Adds context, specificity, and clarity to your prompts
- **Auto-copy**: Enhanced prompts automatically copied to clipboard
- **Error Handling**: Graceful fallback when API is unavailable

#### Smart Response Generation
- **7 Response Types**: General, Educational, Code, Creative, Analytical, Step-by-Step, Fun
- **Context-Aware**: Generates responses based on input type and selected category
- **Global Hotkey**: `Ctrl+Alt+R` for instant smart response generation
- **Clipboard Integration**: Works with selected text or clipboard content

### ⌨️ Global Hotkey System
- **System-Wide Access**: Hotkeys work regardless of active application
- **Configurable Shortcuts**: All hotkeys customizable via settings
- **Default Hotkeys**:
  - `Ctrl+Alt+S`: Toggle dashboard visibility
  - `Ctrl+Alt+N`: Save clipboard as note
  - `Ctrl+Alt+E`: Enhance current prompt
  - `Ctrl+Alt+R`: Generate smart response
- **Thread-Safe**: Proper locking mechanisms prevent conflicts

### 🖥️ Modern User Interface
- **Always-on-Top**: Dashboard stays above other windows
- **Responsive Design**: Adapts to different screen sizes
- **Multiple Layouts**: Single, two, and three-column layouts
- **Dark/Light Themes**: Customizable appearance
- **System Tray Integration**: Minimize to tray with right-click menu
- **Smooth Animations**: Professional UI with loading indicators

### ⚙️ Advanced Configuration
- **Comprehensive Settings**: 50+ configurable options
- **Real-time Updates**: Settings apply immediately without restart
- **Profile System**: Save and load different configuration profiles
- **Validation**: Automatic validation of all settings
- **Backup/Restore**: Export and import settings

## 🚀 Getting Started

### Quick Installation

```bash
# 1. Clone the repository
git clone https://github.com/shakedshoshan/SnapPad.git
cd SnapPad

# 2. Run the automated installer
install.bat
```

### Manual Installation

```bash
# 1. Install Python dependencies
pip install -r requirements.txt

# 2. Copy configuration template
cp config_template.py config.py

# 3. Configure OpenAI API (optional)
# Edit config.py and add your OpenAI API key

# 4. Run the application
python main.py
```

### First-Time Setup

1. **Launch Application**: Run `SnapPad.bat` or `python main.py`
2. **System Tray**: Look for the SnapPad icon in your system tray
3. **Test Hotkeys**: Press `Ctrl+Alt+S` to toggle the dashboard
4. **Configure AI**: Add your OpenAI API key in settings for AI features
5. **Customize**: Adjust settings to match your workflow preferences

## 📊 Value Proposition

### For Developers
- **Code Snippets**: Never lose important code snippets from clipboard
- **API Keys**: Safely store and access API keys and credentials
- **Debug Info**: Capture error messages and debug output
- **Documentation**: Quick access to frequently used documentation
- **AI Code Review**: Use smart responses for code review and improvement

### For Writers & Content Creators
- **Research Notes**: Capture quotes, facts, and references
- **Draft Ideas**: Store writing ideas and outlines
- **Enhanced Prompts**: Improve AI writing prompts for better results
- **Citation Management**: Keep track of sources and citations
- **Creative Writing**: Use AI features for brainstorming and content generation

### For Power Users
- **Workflow Automation**: Streamline repetitive copy-paste tasks
- **Multi-tasking**: Access clipboard history without switching applications
- **Productivity Boost**: Reduce context switching and improve efficiency
- **Data Organization**: Centralized storage for important information
- **Customization**: Tailor the application to specific use cases

### For Teams & Collaboration
- **Shared Notes**: Database can be shared across team members
- **Consistent Workflows**: Standardized hotkeys and settings
- **Knowledge Management**: Centralized repository for team knowledge
- **Training**: Easy onboarding with configurable defaults

## 🔧 Advanced Features

### Database Management
- **Automatic Migration**: Database schema updates handled automatically
- **Data Integrity**: Transaction safety with rollback capabilities
- **Backup Support**: Easy database backup and restoration
- **Performance**: Optimized queries with proper indexing

### Background Services
- **Service Architecture**: Modular design with separate managers
- **Thread Safety**: All operations properly synchronized
- **Resource Management**: Efficient memory and CPU usage
- **Error Recovery**: Graceful handling of service failures

### Security & Privacy
- **Local Storage**: All data stored locally on your machine
- **No Cloud Dependencies**: Works offline (except AI features)
- **API Key Security**: Secure handling of OpenAI API credentials
- **Data Encryption**: Optional encryption for sensitive notes

## 📁 Project Structure

```
SnapPad/
├── main.py                 # Application entry point & orchestration
├── config.py              # Configuration settings & constants
├── database.py            # SQLite operations & data models (813 lines)
├── clipboard_manager.py   # Clipboard monitoring & history (357 lines)
├── hotkey_manager.py      # Global hotkey registration (314 lines)
├── openai_manager.py      # OpenAI API integration (359 lines)
├── ui/                    # User interface components
│   ├── dashboard.py       # Main dashboard window (2878 lines)
│   ├── notes.py          # Notes management interface (821 lines)
│   ├── settings.py       # Settings configuration (699 lines)
│   ├── windows.py        # Window management (1009 lines)
│   ├── components.py     # Reusable UI components (345 lines)
│   └── workers.py        # Background worker threads (95 lines)
├── utils/                 # Utility functions
├── docs/                  # Documentation
├── requirements.txt       # Python dependencies
├── install.bat           # Automated installer
├── SnapPad.bat           # Quick launcher
└── SnapPad_icon.png      # Application icon
```

## 🎯 Performance & Optimization

### Resource Usage
- **Memory**: ~10-20MB typical usage
- **CPU**: Minimal background processing
- **Disk**: ~5MB application + database growth
- **Network**: Only when using AI features

### Optimization Features
- **Efficient Monitoring**: Configurable clipboard check intervals
- **Smart Caching**: Intelligent caching of frequently accessed data
- **Background Processing**: Non-blocking UI operations
- **Memory Management**: Automatic cleanup of old data

## 🔄 Development & Contributing

### Development Setup
```bash
# 1. Clone and setup
git clone https://github.com/shakedshoshan/SnapPad.git
cd SnapPad
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run in development mode
python main.py
```

### Contributing Guidelines
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Make** changes with proper documentation
4. **Test** thoroughly on Windows 10/11
5. **Submit** a pull request with clear description

### Code Quality
- **Type Hints**: Full type annotation coverage
- **Documentation**: Comprehensive docstrings and comments
- **Error Handling**: Robust error handling throughout
- **Testing**: Unit tests for critical components
- **Code Style**: PEP 8 compliance

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🐛 Support & Issues

- **Bug Reports**: [Create an issue](https://github.com/shakedshoshan/SnapPad/issues) with reproduction steps
- **Feature Requests**: [Create an issue](https://github.com/shakedshoshan/SnapPad/issues) with detailed description
- **Questions**: Check existing issues or create a new one
- **Documentation**: See the `docs/` folder for detailed guides

## 🎯 Roadmap

### Completed ✅
- [x] Core clipboard management
- [x] Persistent notes system
- [x] Global hotkey support
- [x] AI prompt enhancement
- [x] Smart response generation
- [x] Modern PyQt6 interface
- [x] System tray integration
- [x] Comprehensive settings

### Planned 🚧
- [ ] Rich text notes support
- [ ] Note categories and tagging
- [ ] Advanced search functionality
- [ ] Cloud synchronization
- [ ] Custom themes & dark mode
- [ ] Multi-language support
- [ ] File attachment support
- [ ] Export/import functionality
- [ ] Plugin system
- [ ] Mobile companion app

---

<div align="center">
<strong>Made with ❤️ for productivity enthusiasts</strong><br>
<sub>Star ⭐ this repo if you find it useful!</sub>
</div> 
