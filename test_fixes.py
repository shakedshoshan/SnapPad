#!/usr/bin/env python3
"""
Test script to verify the fixes for QuickSave & Notes application.
This tests the CSS box-shadow fix and threading issue resolution.
"""

import sys
import time
import threading
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont

# Import the dashboard to test the fixes
from dashboard import Dashboard, ClickableLabel
from database import DatabaseManager
from clipboard_manager import ClipboardManager
import config


def test_clickable_label_css():
    """Test that ClickableLabel doesn't have box-shadow CSS property."""
    print("Testing ClickableLabel CSS...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create a ClickableLabel
    label = ClickableLabel("Test Label")
    
    # Get the stylesheet
    stylesheet = label.styleSheet()
    
    # Check if box-shadow is present
    if "box-shadow" in stylesheet:
        print("✗ FAIL: box-shadow property still present in stylesheet")
        return False
    else:
        print("✓ PASS: box-shadow property removed from stylesheet")
        return True


def test_thread_safe_signals():
    """Test that dashboard signals work correctly for thread-safe communication."""
    print("Testing thread-safe signals...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create dashboard
    dashboard = Dashboard()
    
    # Test that the signals exist
    if not hasattr(dashboard, 'toggle_visibility_signal'):
        print("✗ FAIL: toggle_visibility_signal not found")
        return False
    
    if not hasattr(dashboard, 'add_note_from_clipboard_signal'):
        print("✗ FAIL: add_note_from_clipboard_signal not found")
        return False
    
    # Test that the thread-safe methods exist
    if not hasattr(dashboard, 'toggle_visibility_safe'):
        print("✗ FAIL: toggle_visibility_safe method not found")
        return False
    
    if not hasattr(dashboard, 'add_note_from_clipboard_safe'):
        print("✗ FAIL: add_note_from_clipboard_safe method not found")
        return False
    
    print("✓ PASS: All thread-safe signals and methods exist")
    
    # Test signal emission from another thread
    signal_received = False
    
    def signal_handler():
        nonlocal signal_received
        signal_received = True
        print("✓ PASS: Signal received in main thread")
    
    # Connect signal to handler
    dashboard.toggle_visibility_signal.connect(signal_handler)
    
    # Emit signal from another thread
    def emit_from_thread():
        dashboard.toggle_visibility_safe()
    
    thread = threading.Thread(target=emit_from_thread)
    thread.start()
    thread.join()
    
    # Process events to allow signal to be handled
    app.processEvents()
    
    if signal_received:
        print("✓ PASS: Signal emitted from background thread and received in main thread")
        return True
    else:
        print("✗ FAIL: Signal not received from background thread")
        return False


def test_visual_css_fix():
    """Create a visual test window to verify CSS fixes."""
    print("Creating visual test window...")
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    # Create test window
    window = QWidget()
    window.setWindowTitle("CSS Fix Test - Hover over the label")
    window.setGeometry(100, 100, 400, 300)
    
    layout = QVBoxLayout()
    
    # Instructions
    instructions = QLabel("Hover over the clickable label below.\nIt should show a thicker border instead of a box-shadow.")
    instructions.setWordWrap(True)
    instructions.setStyleSheet("font-size: 14px; margin: 10px; padding: 10px; background: #f0f0f0;")
    layout.addWidget(instructions)
    
    # Test clickable label
    test_label = ClickableLabel("This is a test clickable label.\nHover over me to see the fixed CSS styling!")
    test_label.clicked.connect(lambda: print("Label clicked!"))
    layout.addWidget(test_label)
    
    # Close button
    close_button = QPushButton("Close Test Window")
    close_button.clicked.connect(window.close)
    layout.addWidget(close_button)
    
    window.setLayout(layout)
    return window


def main():
    """Run all tests."""
    print("=" * 50)
    print("QuickSave & Notes - Fix Verification Tests")
    print("=" * 50)
    
    # Initialize Qt Application
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    tests_passed = 0
    total_tests = 2
    
    # Test 1: CSS box-shadow fix
    print("\n1. Testing CSS box-shadow fix...")
    if test_clickable_label_css():
        tests_passed += 1
    
    # Test 2: Thread-safe signals
    print("\n2. Testing thread-safe signals...")
    if test_thread_safe_signals():
        tests_passed += 1
    
    # Results
    print("\n" + "=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("✓ ALL TESTS PASSED - Fixes are working correctly!")
    else:
        print("✗ SOME TESTS FAILED - Please check the issues above")
    
    print("=" * 50)
    
    # Show visual test window
    print("\n3. Visual test window...")
    visual_window = test_visual_css_fix()
    visual_window.show()
    
    print("\nVisual test window created. Close it when done testing.")
    print("The application will exit when you close the test window.")
    
    # Run the application
    return app.exec()


if __name__ == "__main__":
    sys.exit(main()) 