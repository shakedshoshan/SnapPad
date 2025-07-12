#!/usr/bin/env python3
"""
SnapPad - Main Application
A lightweight Windows application for clipboard history and persistent notes.
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
    """Background service that runs the clipboard monitoring and hotkey management."""
    
    def __init__(self, clipboard_manager, hotkey_manager):
        super().__init__()
        self.clipboard_manager = clipboard_manager
        self.hotkey_manager = hotkey_manager
        self.running = True
    
    def run(self):
        """Run the background service."""
        print("Background service starting...")
        
        # Start clipboard monitoring
        self.clipboard_manager.start_monitoring()
        
        # Start hotkey monitoring
        self.hotkey_manager.start_monitoring()
        
        # Keep the service running
        while self.running:
            time.sleep(1)
        
        print("Background service stopping...")
        self.cleanup()
    
    def stop(self):
        """Stop the background service."""
        self.running = False
        self.wait()
    
    def cleanup(self):
        """Clean up resources."""
        self.clipboard_manager.stop_monitoring()
        self.hotkey_manager.stop_monitoring()


class SnapPadApp:
    """Main application class that coordinates all components."""
    
    def __init__(self):
        self.app = None
        self.dashboard = None
        self.database_manager = None
        self.clipboard_manager = None
        self.hotkey_manager = None
        self.background_service = None
        self.system_tray = None
        
        # Initialize application
        self.init_app()
        self.init_managers()
        self.init_dashboard()
        self.init_hotkeys()
        self.init_system_tray()
        self.init_background_service()
    
    def init_app(self):
        """Initialize the Qt application."""
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)  # Keep running when window is closed
        
        # Set application properties
        self.app.setApplicationName("SnapPad")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("SnapPad")
        
        print("Qt Application initialized")
    
    def init_managers(self):
        """Initialize the core managers."""
        # Database manager
        self.database_manager = DatabaseManager()
        print("Database manager initialized")
        
        # Clipboard manager
        self.clipboard_manager = ClipboardManager(max_history=config.CLIPBOARD_HISTORY_SIZE)
        print("Clipboard manager initialized")
        
        # Hotkey manager
        self.hotkey_manager = HotkeyManager()
        print("Hotkey manager initialized")
    
    def init_dashboard(self):
        """Initialize the dashboard UI."""
        self.dashboard = Dashboard()
        self.dashboard.set_managers(self.clipboard_manager, self.database_manager)
        # Show the dashboard when the application first runs
        self.dashboard.show()
        print("Dashboard initialized and shown")
    
    def init_hotkeys(self):
        """Initialize global hotkeys."""
        print(f"Registering hotkey: {config.HOTKEY_TOGGLE_DASHBOARD}")
        # Test if the hotkey is valid
        if not self.hotkey_manager.test_hotkey(config.HOTKEY_TOGGLE_DASHBOARD):
            print(f"WARNING: Invalid hotkey format: {config.HOTKEY_TOGGLE_DASHBOARD}")
            
        # Toggle dashboard visibility
        self.hotkey_manager.register_hotkey(
            config.HOTKEY_TOGGLE_DASHBOARD,
            self.dashboard.toggle_visibility_safe,
            "Toggle dashboard visibility"
        )
        
        print(f"Registering hotkey: {config.HOTKEY_SAVE_NOTE}")
        # Test if the hotkey is valid
        if not self.hotkey_manager.test_hotkey(config.HOTKEY_SAVE_NOTE):
            print(f"WARNING: Invalid hotkey format: {config.HOTKEY_SAVE_NOTE}")
            
        # Add note from selected text
        self.hotkey_manager.register_hotkey(
            config.HOTKEY_SAVE_NOTE,
            self.dashboard.add_note_from_clipboard_safe,
            "Add note from selected text"
        )
        
        print("Hotkeys registered:")
        for hotkey, description in self.hotkey_manager.get_registered_hotkeys().items():
            print(f"  {hotkey}: {description}")
    
    def init_system_tray(self):
        """Initialize the system tray icon."""
        if not config.SYSTEM_TRAY_ENABLED or not QSystemTrayIcon.isSystemTrayAvailable():
            print("System tray not available or disabled")
            return
        
        self.system_tray = QSystemTrayIcon()
        
        # Create tray menu
        tray_menu = QMenu()
        
        # Show/Hide Dashboard
        show_action = QAction("Show Dashboard", self.app)
        show_action.triggered.connect(self.dashboard.show)
        tray_menu.addAction(show_action)
        
        hide_action = QAction("Hide Dashboard", self.app)
        hide_action.triggered.connect(self.dashboard.hide)
        tray_menu.addAction(hide_action)
        
        tray_menu.addSeparator()
        
        # Clear clipboard history
        clear_clipboard_action = QAction("Clear Clipboard History", self.app)
        clear_clipboard_action.triggered.connect(self.clipboard_manager.clear_history)
        tray_menu.addAction(clear_clipboard_action)
        
        tray_menu.addSeparator()
        
        # About
        about_action = QAction("About", self.app)
        about_action.triggered.connect(self.show_about)
        tray_menu.addAction(about_action)
        
        # Exit
        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(exit_action)
        
        self.system_tray.setContextMenu(tray_menu)
        
        # Set tray icon (using a simple text icon for now)
        self.system_tray.setToolTip(config.SYSTEM_TRAY_TOOLTIP)
        
        # Connect double-click to show dashboard
        self.system_tray.activated.connect(self.on_tray_activated)
        
        # Show the tray icon
        self.system_tray.show()
        print("System tray initialized")
    
    def init_background_service(self):
        """Initialize and start the background service."""
        self.background_service = BackgroundService(
            self.clipboard_manager,
            self.hotkey_manager
        )
        self.background_service.start()
        print("Background service started")
    
    def on_tray_activated(self, reason):
        """Handle system tray activation."""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.dashboard.toggle_visibility_safe()
    
    def show_about(self):
        """Show about dialog."""
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
        """Quit the application gracefully."""
        print("Shutting down application...")
        
        # Stop background service
        if self.background_service:
            self.background_service.stop()
        
        # Hide system tray
        if self.system_tray:
            self.system_tray.hide()
        
        # Quit the application
        self.app.quit()
    
    def run(self):
        """Run the application."""
        print("SnapPad starting...")
        print(f"Press {config.HOTKEY_TOGGLE_DASHBOARD} to toggle dashboard")
        print(f"Press {config.HOTKEY_SAVE_NOTE} to save clipboard as note")
        print("Check system tray for more options")
        
        if config.DEBUG_MODE:
            print(config.get_config_summary())
        
        # Handle system signals for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Make sure dashboard is visible and in front
        self.dashboard.show()
        self.dashboard.raise_()
        self.dashboard.activateWindow()
        
        # Run the application
        return self.app.exec()
    
    def signal_handler(self, signum, frame):
        """Handle system signals."""
        print(f"Received signal {signum}, shutting down...")
        self.quit_application()


def main():
    """Main entry point."""
    try:
        app = SnapPadApp()
        return app.run()
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 