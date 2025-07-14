#!/usr/bin/env python3
"""
SnapPad - Main Application Entry Point

This is the main entry point for SnapPad, a lightweight Windows application that provides:
- Clipboard history management
- Persistent notes storage
- Global hotkey support
- System tray integration
- Always-on-top dashboard interface

The application uses PyQt6 for the GUI, SQLite for data storage, and runs background
services for clipboard monitoring and hotkey management.

Author: SnapPad Team
Version: 1.0.0
Platform: Windows 10/11
"""

import sys
import os
import signal
import time
from PyQt6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QAction

# Import our custom modules
from database import DatabaseManager
from clipboard_manager import ClipboardManager
from hotkey_manager import HotkeyManager
from dashboard import Dashboard
import config


class BackgroundService(QThread):
    """
    Background service that runs clipboard monitoring and hotkey management.
    
    This service runs in a separate thread to avoid blocking the main GUI thread.
    It coordinates between the clipboard manager and hotkey manager to provide
    seamless background functionality.
    
    Key responsibilities:
    - Start and maintain clipboard monitoring
    - Handle global hotkey registration and monitoring
    - Manage service lifecycle (start/stop)
    - Clean up resources on shutdown
    """
    
    def __init__(self, clipboard_manager, hotkey_manager):
        """
        Initialize the background service.
        
        Args:
            clipboard_manager (ClipboardManager): Handles clipboard monitoring
            hotkey_manager (HotkeyManager): Handles global hotkey registration
        """
        super().__init__()
        self.clipboard_manager = clipboard_manager
        self.hotkey_manager = hotkey_manager
        self.running = True
    
    def run(self):
        """
        Main service loop that runs in the background thread.
        
        This method:
        1. Starts clipboard monitoring
        2. Starts hotkey monitoring
        3. Keeps the service alive with a sleep loop
        4. Handles cleanup when stopping
        """
        print("Background service starting...")
        
        # Start clipboard monitoring in its own thread
        self.clipboard_manager.start_monitoring()
        
        # Start hotkey monitoring in its own thread
        self.hotkey_manager.start_monitoring()
        
        # Keep the service running with a simple loop
        # This prevents the thread from exiting while services are active
        while self.running:
            time.sleep(1)  # Sleep for 1 second between checks
        
        print("Background service stopping...")
        self.cleanup()
    
    def stop(self):
        """
        Stop the background service gracefully.
        
        This sets the running flag to False and waits for the thread to finish.
        """
        self.running = False
        self.wait()  # Wait for the thread to finish
    
    def cleanup(self):
        """
        Clean up resources when the service stops.
        
        This ensures proper shutdown of:
        - Clipboard monitoring thread
        - Hotkey monitoring thread
        - Any other resources
        """
        self.clipboard_manager.stop_monitoring()
        self.hotkey_manager.stop_monitoring()


class SnapPadApp:
    """
    Main application class that coordinates all components.
    
    This is the central orchestrator that:
    - Initializes the Qt application
    - Creates and manages all core components
    - Handles system tray integration
    - Manages application lifecycle
    - Provides graceful shutdown
    
    The application follows a component-based architecture where each major
    functionality is handled by a dedicated manager class.
    """
    
    def __init__(self):
        """
        Initialize the main application.
        
        This constructor sets up all application components in the correct order:
        1. Qt application initialization
        2. Core managers (database, clipboard, hotkeys)
        3. Dashboard UI
        4. Hotkey registration
        5. System tray setup
        6. Background service startup
        """
        # Initialize all component references
        self.app = None
        self.dashboard = None
        self.database_manager = None
        self.clipboard_manager = None
        self.hotkey_manager = None
        self.background_service = None
        self.system_tray = None
        
        # Initialize application components in dependency order
        self.init_app()
        self.init_managers()
        self.init_dashboard()
        self.init_hotkeys()
        self.init_system_tray()
        self.init_background_service()
    
    def init_app(self):
        """
        Initialize the Qt application and set basic properties.
        
        This method:
        - Creates the QApplication instance
        - Sets application metadata (name, version, organization)
        - Configures the application to continue running when windows are closed
        """
        self.app = QApplication(sys.argv)
        
        # Keep the application running even when all windows are closed
        # This is important for system tray functionality
        self.app.setQuitOnLastWindowClosed(False)
        
        # Set application metadata for proper identification
        self.app.setApplicationName("SnapPad")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("SnapPad")
        
        print("Qt Application initialized")
    
    def init_managers(self):
        """
        Initialize the core manager classes.
        
        These managers handle the core functionality:
        - DatabaseManager: SQLite database operations for notes
        - ClipboardManager: Clipboard monitoring and history
        - HotkeyManager: Global hotkey registration and handling
        
        Order matters here as some managers may depend on others.
        """
        # Database manager - handles SQLite operations for persistent notes
        self.database_manager = DatabaseManager()
        print("Database manager initialized")
        
        # Clipboard manager - monitors clipboard changes and maintains history
        self.clipboard_manager = ClipboardManager(max_history=config.CLIPBOARD_HISTORY_SIZE)
        print("Clipboard manager initialized")
        
        # Hotkey manager - handles global keyboard shortcuts
        self.hotkey_manager = HotkeyManager()
        print("Hotkey manager initialized")
    
    def init_dashboard(self):
        """
        Initialize the dashboard UI.
        
        The dashboard is the main user interface that provides:
        - Clipboard history display
        - Notes management interface
        - Always-on-top positioning
        - Compact, side-mounted design
        
        We connect the dashboard to the managers so it can interact with data.
        """
        self.dashboard = Dashboard()
        
        # Connect the dashboard to our data managers
        self.dashboard.set_managers(self.clipboard_manager, self.database_manager)
        
        # Show the dashboard when the application first runs
        # Users can hide it later using hotkeys or system tray
        self.dashboard.show()
        print("Dashboard initialized and shown")
    
    def init_hotkeys(self):
        """
        Initialize global hotkeys for the application.
        
        This method registers the configured hotkeys:
        - Toggle dashboard visibility (default: Ctrl+Alt+S)
        - Save clipboard content as note (default: Ctrl+Alt+N)
        
        Each hotkey is validated before registration to ensure it's properly formatted.
        """
        # Register the dashboard toggle hotkey
        print(f"Registering hotkey: {config.HOTKEY_TOGGLE_DASHBOARD}")
        
        # Test if the hotkey format is valid before registration
        if not self.hotkey_manager.test_hotkey(config.HOTKEY_TOGGLE_DASHBOARD):
            print(f"WARNING: Invalid hotkey format: {config.HOTKEY_TOGGLE_DASHBOARD}")
            
        # Register the hotkey with a thread-safe callback
        self.hotkey_manager.register_hotkey(
            config.HOTKEY_TOGGLE_DASHBOARD,
            self.dashboard.toggle_visibility_safe,  # Thread-safe wrapper
            "Toggle dashboard visibility"
        )
        
        # Register the save note hotkey
        print(f"Registering hotkey: {config.HOTKEY_SAVE_NOTE}")
        
        # Test if the hotkey format is valid before registration
        if not self.hotkey_manager.test_hotkey(config.HOTKEY_SAVE_NOTE):
            print(f"WARNING: Invalid hotkey format: {config.HOTKEY_SAVE_NOTE}")
            
        # Register the hotkey to save current clipboard as a note
        self.hotkey_manager.register_hotkey(
            config.HOTKEY_SAVE_NOTE,
            self.dashboard.add_note_from_clipboard_safe,  # Thread-safe wrapper
            "Add note from selected text"
        )
        
        # Display all registered hotkeys for user reference
        print("Hotkeys registered:")
        for hotkey, description in self.hotkey_manager.get_registered_hotkeys().items():
            print(f"  {hotkey}: {description}")
    
    def init_system_tray(self):
        """
        Initialize the system tray icon and menu.
        
        The system tray provides:
        - Quick access to show/hide dashboard
        - Clipboard history management
        - About dialog
        - Application exit
        
        The tray icon allows the application to run in the background
        without cluttering the taskbar.
        """
        # Check if system tray is available and enabled
        if not config.SYSTEM_TRAY_ENABLED or not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray not available or disabled")
            return
        
        # Create the system tray icon
        self.system_tray = QSystemTrayIcon()
        
        # Create the context menu for the tray icon
        tray_menu = QMenu()
        
        # Show Dashboard action
        show_action = QAction("Show Dashboard", self.app)
        show_action.triggered.connect(self.dashboard.show)
        tray_menu.addAction(show_action)
        
        # Hide Dashboard action
        hide_action = QAction("Hide Dashboard", self.app)
        hide_action.triggered.connect(self.dashboard.hide)
        tray_menu.addAction(hide_action)
        
        # Separator for visual grouping
        tray_menu.addSeparator()
        
        # Clear clipboard history action
        clear_clipboard_action = QAction("Clear Clipboard History", self.app)
        clear_clipboard_action.triggered.connect(self.clipboard_manager.clear_history)
        tray_menu.addAction(clear_clipboard_action)
        
        # Another separator
        tray_menu.addSeparator()
        
        # About dialog action
        about_action = QAction("About", self.app)
        about_action.triggered.connect(self.show_about)
        tray_menu.addAction(about_action)
        
        # Exit application action
        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        # Attach the menu to the tray icon
        self.system_tray.setContextMenu(tray_menu)
        
        # Set the tooltip text shown when hovering over the tray icon
        self.system_tray.setToolTip(config.SYSTEM_TRAY_TOOLTIP)
        
        # Connect double-click events to toggle dashboard visibility
        self.system_tray.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.system_tray.show()
        print("System tray initialized")
    
    def init_background_service(self):
        """
        Initialize and start the background service.
        
        The background service runs in a separate thread and handles:
        - Clipboard monitoring
        - Hotkey monitoring
        - Other background tasks
        
        This separation ensures the GUI remains responsive while background
        operations continue.
        """
        self.background_service = BackgroundService(
            self.clipboard_manager,
            self.hotkey_manager
        )
        
        # Start the background service thread
        self.background_service.start()
        print("Background service started")
    
    def on_tray_activated(self, reason):
        """
        Handle system tray icon activation events.
        
        Args:
            reason (QSystemTrayIcon.ActivationReason): The type of activation
        
        Currently handles:
        - Double-click: Toggle dashboard visibility
        """
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.dashboard.toggle_visibility_safe()
    
    def show_about(self):
        """
        Show the about dialog with application information.
        
        This displays:
        - Application name and version
        - Feature overview
        - Hotkey reference
        - Data storage location
        """
        from PyQt6.QtWidgets import QMessageBox
        
        about_text = """
        SnapPad v1.0.0
        
        A lightweight Windows application for clipboard history and persistent notes.
        
        Features:
        • Clipboard history (last 10 items)
        • Persistent notes with SQLite storage
        • Global hotkeys (Ctrl+Alt+S, Ctrl+Alt+N)
        • Always-on-top side dashboard
        
        Hotkeys:
        • Ctrl+Alt+S: Toggle dashboard
        • Ctrl+Alt+N: Save selected text as note
        
        Data stored in: %APPDATA%\\SnapPad
        """
        
        QMessageBox.about(self.dashboard, "About SnapPad", about_text)
    
    def quit_application(self):
        """
        Quit the application gracefully.
        
        This method ensures proper cleanup of all resources:
        1. Stop background service
        2. Hide system tray icon
        3. Exit the Qt application
        
        This prevents resource leaks and ensures clean shutdown.
        """
        print("Shutting down application...")
        
        # Stop the background service first
        if self.background_service:
            self.background_service.stop()
        
        # Hide the system tray icon
        if self.system_tray:
            self.system_tray.hide()
        
        # Exit the Qt application
        self.app.quit()
    
    def run(self):
        """
        Run the application.
        
        This is the main application loop that:
        1. Displays startup information
        2. Sets up signal handlers for graceful shutdown
        3. Ensures the dashboard is visible and active
        4. Starts the Qt event loop
        
        Returns:
            int: Exit code (0 for success, non-zero for error)
        """
        print("SnapPad starting...")
        print(f"Press {config.HOTKEY_TOGGLE_DASHBOARD} to toggle dashboard")
        print(f"Press {config.HOTKEY_SAVE_NOTE} to save clipboard as note")
        print("Check system tray for more options")
        
        # Show configuration summary if debug mode is enabled
        if config.DEBUG_MODE:
            print(config.get_config_summary())
        
        # Handle system signals for graceful shutdown
        # This allows the application to clean up when terminated
        signal.signal(signal.SIGINT, self.signal_handler)   # Ctrl+C
        signal.signal(signal.SIGTERM, self.signal_handler)  # Termination signal
        
        # Ensure the dashboard is visible and in front when starting
        self.dashboard.show()
        self.dashboard.raise_()         # Bring window to front
        self.dashboard.activateWindow() # Make it the active window
        
        # Start the Qt event loop - this blocks until the application exits
        return self.app.exec()
    
    def signal_handler(self, signum, frame):
        """
        Handle system signals for graceful shutdown.
        
        Args:
            signum (int): Signal number
            frame: Current stack frame
        
        This ensures the application shuts down properly when receiving 
        system signals like SIGINT (Ctrl+C) or SIGTERM.
        """
        print(f"Received signal {signum}, shutting down...")
        self.quit_application()


def main():
    """
    Main entry point for the application.
    
    This function:
    1. Creates the main application instance
    2. Runs the application
    3. Handles any top-level exceptions
    4. Returns appropriate exit codes
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    try:
        # Create and run the application
        app = SnapPadApp()
        return app.run()
    except Exception as e:
        print(f"Error: {e}")
        return 1


# Application entry point
if __name__ == "__main__":
    # Exit with the return code from main()
    sys.exit(main()) 