"""
Settings Window for SnapPad

This module contains the settings window that allows users to configure
dashboard features, their order, and layout.
"""

import json
import os
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QPushButton, QListWidget, QListWidgetItem,
                             QComboBox, QSpinBox, QCheckBox, QFrame, QMessageBox,
                             QApplication, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class SettingsWindow(QMainWindow):
    """
    Settings window for configuring dashboard features and layout.
    
    This window provides:
    - Enable/disable dashboard features
    - Reorder features
    - Configure column layout (1-3 columns)
    - Save/load settings
    """
    
    # Signal emitted when settings are changed
    settings_changed = pyqtSignal(dict)
    
    def __init__(self, parent=None):
        """
        Initialize the settings window.
        
        Args:
            parent: Parent widget (usually the main Dashboard)
        """
        super().__init__(parent)
        self.parent_dashboard = parent
        
        # Default settings
        self.default_settings = {
            'features': [
                {'id': 'clipboard', 'name': '📋 Clipboard History', 'enabled': True, 'order': 0},
                {'id': 'notes', 'name': '📝 Notes', 'enabled': True, 'order': 1},
                {'id': 'prompt_enhancement', 'name': '🤖 AI Prompt Enhancement', 'enabled': True, 'order': 2},
                {'id': 'smart_response', 'name': '🧠 AI Smart Response', 'enabled': True, 'order': 3}
            ],
            'columns': 1,
            'max_features_per_column': 3,
            'smart_response_visibility': 'popup'
        }
        
        # Current settings
        self.current_settings = self.load_settings()
        
        # Setup UI and window properties
        self.setup_ui()
        self.setup_window_properties()
        self.load_current_settings()
    
    def setup_ui(self):
        """
        Set up the user interface for the settings window.
        """
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Set window styling
        self.setStyleSheet("""
            QMainWindow {
                background: #f8f9fa;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)
        
        # Title
        title = QLabel("⚙️ Dashboard Settings")
        title.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 16px;
                color: #2c3e50;
                margin-bottom: 8px;
                background: transparent;
            }
        """)
        main_layout.addWidget(title)
        
        # Features Section
        features_frame = QFrame()
        features_frame.setFrameStyle(QFrame.Shape.Box)
        features_frame.setStyleSheet("""
            QFrame {
                border: 1px solid #d1d5db;
                border-radius: 8px;
                background: #ffffff;
                padding: 6px;
            }
        """)
        features_layout = QVBoxLayout()
        features_layout.setSpacing(8)
        features_layout.setContentsMargins(12, 12, 12, 12)
        
        # Features header
        features_header = QLabel("Dashboard Features")
        features_header.setStyleSheet("""
            QLabel {
                font-weight: bold; 
                font-size: 14px;
                color: #2c3e50;
                margin-bottom: 5px;
                background: transparent;
            }
        """)
        features_layout.addWidget(features_header)
        
        # Features description
        features_desc = QLabel("Enable/disable features and reorder them by dragging:")
        features_desc.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #7f8c8d;
                background: transparent;
            }
        """)
        features_layout.addWidget(features_desc)
        
        # Features list
        self.features_list = QListWidget()
        self.features_list.setDragDropMode(QListWidget.DragDropMode.InternalMove)
        self.features_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                background: #ffffff;
                padding: 4px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f1f3f4;
                background: #ffffff;
            }
            QListWidget::item:selected {
                background: #e3f2fd;
                color: #2c3e50;
            }
            QListWidget::item:hover {
                background: #f8f9fa;
            }
        """)
        features_layout.addWidget(self.features_list)
        
        # Feature controls
        feature_controls_layout = QHBoxLayout()
        feature_controls_layout.setSpacing(10)
        
        # Enable/disable button
        self.toggle_feature_btn = QPushButton("Toggle Feature")
        self.toggle_feature_btn.clicked.connect(self.toggle_selected_feature)
        self.toggle_feature_btn.setStyleSheet("""
            QPushButton {
                background: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #2980b9;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        # Move up button
        self.move_up_btn = QPushButton("↑ Move Up")
        self.move_up_btn.clicked.connect(self.move_feature_up)
        self.move_up_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        # Move down button
        self.move_down_btn = QPushButton("↓ Move Down")
        self.move_down_btn.clicked.connect(self.move_feature_down)
        self.move_down_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
            QPushButton:disabled {
                background: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        
        feature_controls_layout.addWidget(self.toggle_feature_btn)
        feature_controls_layout.addWidget(self.move_up_btn)
        feature_controls_layout.addWidget(self.move_down_btn)
        feature_controls_layout.addStretch()
        
        features_layout.addLayout(feature_controls_layout)
        features_frame.setLayout(features_layout)
        main_layout.addWidget(features_frame)
        
        # Layout Configuration Section (Compact)
        layout_layout = QHBoxLayout()
        layout_layout.setSpacing(15)
        layout_layout.setContentsMargins(0, 5, 0, 5)
        
        # Columns setting
        columns_layout = QHBoxLayout()
        columns_layout.setSpacing(8)
        
        columns_label = QLabel("📐 Columns:")
        columns_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #2c3e50;
                background: transparent;
                font-weight: bold;
            }
        """)
        
        self.columns_spinbox = QSpinBox()
        self.columns_spinbox.setMinimum(1)
        self.columns_spinbox.setMaximum(3)
        self.columns_spinbox.setValue(1)
        self.columns_spinbox.setStyleSheet("""
            QSpinBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 11px;
                background-color: #ffffff;
                color: #2c3e50;
                min-width: 50px;
            }
            QSpinBox:focus {
                border-color: #4a90e2;
            }
        """)
        self.columns_spinbox.valueChanged.connect(self.on_columns_changed)
        
        columns_layout.addWidget(columns_label)
        columns_layout.addWidget(self.columns_spinbox)
        
        # Max features setting
        max_features_layout = QHBoxLayout()
        max_features_layout.setSpacing(8)
        
        max_features_label = QLabel("Max/col:")
        max_features_label.setStyleSheet("""
            QLabel {
                font-size: 11px;
                color: #2c3e50;
                background: transparent;
                font-weight: bold;
            }
        """)
        
        self.max_features_spinbox = QSpinBox()
        self.max_features_spinbox.setMinimum(1)
        self.max_features_spinbox.setMaximum(3)
        self.max_features_spinbox.setValue(3)
        self.max_features_spinbox.setStyleSheet("""
            QSpinBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 6px;
                font-size: 11px;
                background-color: #ffffff;
                color: #2c3e50;
                min-width: 50px;
            }
            QSpinBox:focus {
                border-color: #4a90e2;
            }
        """)
        
        max_features_layout.addWidget(max_features_label)
        max_features_layout.addWidget(self.max_features_spinbox)
        
        # Preview info
        self.layout_preview_label = QLabel("Single column • 360px")
        self.layout_preview_label.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #7f8c8d;
                background: transparent;
                font-style: italic;
            }
        """)
        
        layout_layout.addLayout(columns_layout)
        layout_layout.addLayout(max_features_layout)
        layout_layout.addWidget(self.layout_preview_label)
        layout_layout.addStretch()
        
        main_layout.addLayout(layout_layout)
        
        # Smart Response Settings Section (Compact)
        smart_response_layout = QHBoxLayout()
        smart_response_layout.setSpacing(10)
        smart_response_layout.setContentsMargins(0, 5, 0, 5)
        
        # Smart response label
        smart_response_label = QLabel("🧠 Smart Response:")
        smart_response_label.setStyleSheet("""
            QLabel {
                font-size: 12px;
                color: #2c3e50;
                background: transparent;
                font-weight: bold;
            }
        """)
        
        self.visibility_combo = QComboBox()
        self.visibility_combo.addItem("Show Popup", "popup")
        self.visibility_combo.addItem("Hidden", "hidden")
        self.visibility_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #d1d5db;
                border-radius: 4px;
                padding: 4px 8px;
                font-size: 11px;
                background-color: #ffffff;
                color: #2c3e50;
                min-width: 100px;
            }
            QComboBox:focus {
                border-color: #4a90e2;
            }
        """)
        
        # Help text
        help_text = QLabel("(Hidden: no feedback, Popup: shows dialog)")
        help_text.setStyleSheet("""
            QLabel {
                font-size: 10px;
                color: #7f8c8d;
                background: transparent;
                font-style: italic;
            }
        """)
        
        smart_response_layout.addWidget(smart_response_label)
        smart_response_layout.addWidget(self.visibility_combo)
        smart_response_layout.addWidget(help_text)
        smart_response_layout.addStretch()
        
        main_layout.addLayout(smart_response_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(8)
        buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        # Reset to defaults button
        self.reset_btn = QPushButton("Reset to Defaults")
        self.reset_btn.clicked.connect(self.reset_to_defaults)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background: #e67e22;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #d35400;
            }
        """)
        
        # Save button
        self.save_btn = QPushButton("Save Settings")
        self.save_btn.clicked.connect(self.save_settings)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #229954;
            }
        """)
        
        # Close button
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background: #95a5a6;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 12px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #7f8c8d;
            }
        """)
        
        buttons_layout.addWidget(self.reset_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_btn)
        buttons_layout.addWidget(self.close_btn)
        
        main_layout.addLayout(buttons_layout)
        
        central_widget.setLayout(main_layout)
    
    def setup_window_properties(self):
        """
        Configure window properties for the settings window.
        """
        self.setWindowTitle("SnapPad - Settings")
        self.setMinimumSize(480, 550)
        self.resize(520, 600)
        
        # Center window on screen
        screen = QApplication.primaryScreen()
        screen_geometry = screen.geometry()
        
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
        
        # Set window flags
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint)
    
    def load_settings(self):
        """
        Load settings from file or return defaults.
        
        Returns:
            dict: Current settings
        """
        settings_file = os.path.join(os.path.expanduser("~"), ".snappad_settings.json")
        
        try:
            if os.path.exists(settings_file):
                with open(settings_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading settings: {e}")
        
        return self.default_settings.copy()
    
    def save_settings(self):
        """
        Save current settings to file and update config.py.
        """
        settings_file = os.path.join(os.path.expanduser("~"), ".snappad_settings.json")
        
        try:
            # Update settings from UI
            self.update_settings_from_ui()
            
            # Save to JSON file
            with open(settings_file, 'w') as f:
                json.dump(self.current_settings, f, indent=2)
            
            # Update config.py with smart response visibility setting
            self.update_config_file()
            
            # Emit signal to notify parent
            self.settings_changed.emit(self.current_settings)
            
            QMessageBox.information(self, "Settings Saved", 
                                  "Settings have been saved successfully!")
            
            print("Settings saved successfully")
            
        except Exception as e:
            QMessageBox.warning(self, "Save Error", 
                              f"Failed to save settings: {str(e)}")
            print(f"Error saving settings: {e}")
    
    def update_config_file(self):
        """
        Update config.py with the smart response visibility setting.
        """
        try:
            config_file = "config.py"
            if not os.path.exists(config_file):
                print("Config file not found, skipping config update")
                return
            
            # Read current config file
            with open(config_file, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            # Get the new visibility setting
            visibility = self.current_settings.get('smart_response_visibility', 'popup')
            
            # Update the SMART_RESPONSE_VISIBILITY line
            import re
            pattern = r'SMART_RESPONSE_VISIBILITY\s*=\s*["\']([^"\']+)["\']'
            replacement = f'SMART_RESPONSE_VISIBILITY = "{visibility}"'
            
            if re.search(pattern, config_content):
                # Replace existing setting
                new_content = re.sub(pattern, replacement, config_content)
            else:
                # Add setting after SMART_RESPONSE_DEFAULT_TYPE
                pattern = r'(SMART_RESPONSE_DEFAULT_TYPE\s*=\s*["\'][^"\']+["\']\s*\n)'
                replacement = f'\\1\n# Smart response visibility mode\n# Options: "hidden" - show nothing, no spinner or popup\n#          "popup" - show loading spinner and popup with response\nSMART_RESPONSE_VISIBILITY = "{visibility}"\n\n'
                new_content = re.sub(pattern, replacement, config_content)
            
            # Write updated config file
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"Config file updated with SMART_RESPONSE_VISIBILITY = {visibility}")
            
        except Exception as e:
            print(f"Error updating config file: {e}")
    
    def load_current_settings(self):
        """
        Load current settings into the UI.
        """
        # Load features into list
        self.features_list.clear()
        for feature in self.current_settings['features']:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, feature)
            
            # Create display text with enabled/disabled indicator
            status = "✓" if feature['enabled'] else "✗"
            display_text = f"{status} {feature['name']}"
            
            item.setText(display_text)
            self.features_list.addItem(item)
        
        # Load layout settings
        self.columns_spinbox.setValue(self.current_settings['columns'])
        self.max_features_spinbox.setValue(self.current_settings['max_features_per_column'])
        
        # Load smart response settings
        visibility = self.current_settings.get('smart_response_visibility', 'popup')
        index = self.visibility_combo.findData(visibility)
        if index >= 0:
            self.visibility_combo.setCurrentIndex(index)
        
        # Update preview
        self.update_layout_preview()
    
    def update_settings_from_ui(self):
        """
        Update current settings from UI values.
        """
        # Update features
        features = []
        for i in range(self.features_list.count()):
            item = self.features_list.item(i)
            feature_data = item.data(Qt.ItemDataRole.UserRole)
            feature_data['order'] = i
            features.append(feature_data)
        
        self.current_settings['features'] = features
        
        # Update layout settings
        self.current_settings['columns'] = self.columns_spinbox.value()
        self.current_settings['max_features_per_column'] = self.max_features_spinbox.value()
        
        # Update smart response settings
        self.current_settings['smart_response_visibility'] = self.visibility_combo.currentData()
    
    def toggle_selected_feature(self):
        """
        Toggle the enabled state of the selected feature.
        """
        current_item = self.features_list.currentItem()
        if not current_item:
            return
        
        feature_data = current_item.data(Qt.ItemDataRole.UserRole)
        feature_data['enabled'] = not feature_data['enabled']
        
        # Update display
        status = "✓" if feature_data['enabled'] else "✗"
        display_text = f"{status} {feature_data['name']}"
        current_item.setText(display_text)
        
        # Update item data
        current_item.setData(Qt.ItemDataRole.UserRole, feature_data)
    
    def move_feature_up(self):
        """
        Move the selected feature up in the list.
        """
        current_row = self.features_list.currentRow()
        if current_row > 0:
            item = self.features_list.takeItem(current_row)
            self.features_list.insertItem(current_row - 1, item)
            self.features_list.setCurrentItem(item)
    
    def move_feature_down(self):
        """
        Move the selected feature down in the list.
        """
        current_row = self.features_list.currentRow()
        if current_row < self.features_list.count() - 1:
            item = self.features_list.takeItem(current_row)
            self.features_list.insertItem(current_row + 1, item)
            self.features_list.setCurrentItem(item)
    
    def on_columns_changed(self):
        """
        Handle column count change.
        """
        self.update_layout_preview()
    
    def update_layout_preview(self):
        """
        Update the layout preview text.
        """
        columns = self.columns_spinbox.value()
        max_features = self.max_features_spinbox.value()
        
        if columns == 1:
            layout_type = "Single column"
            expected_width = 360
        elif columns == 2:
            layout_type = "Two columns"
            expected_width = 576
        else:
            layout_type = "Three columns"
            expected_width = 792
        
        preview_text = f"{layout_type} • {expected_width}px"
        self.layout_preview_label.setText(preview_text)
    
    def reset_to_defaults(self):
        """
        Reset settings to defaults.
        """
        reply = QMessageBox.question(self, "Reset Settings", 
                                   "Are you sure you want to reset all settings to defaults?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            self.current_settings = self.default_settings.copy()
            self.load_current_settings()
            print("Settings reset to defaults")
    
    def get_settings(self):
        """
        Get current settings.
        
        Returns:
            dict: Current settings
        """
        self.update_settings_from_ui()
        return self.current_settings.copy() 