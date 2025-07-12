#!/usr/bin/env python3
"""
Test script for QuickSave & Notes application components.
This script tests the core functionality without requiring user interaction.
"""

import sys
import os
import time
import tempfile
import threading
from unittest.mock import Mock, patch
import unittest
import os
import sys
import time
from database import DatabaseManager
from clipboard_manager import ClipboardManager
from hotkey_manager import HotkeyManager
import config


# Add the current directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Test imports
def test_imports():
    """Test that all required modules can be imported."""
    print("Testing imports...")
    
    try:
        import config
        print("✓ config module imported successfully")
        
        from database import DatabaseManager
        print("✓ database module imported successfully")
        
        from clipboard_manager import ClipboardManager
        print("✓ clipboard_manager module imported successfully")
        
        from hotkey_manager import HotkeyManager
        print("✓ hotkey_manager module imported successfully")
        
        # Skip dashboard import test as it requires display
        print("✓ All core modules imported successfully")
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_database():
    """Test database operations."""
    print("\nTesting database operations...")
    
    try:
        # Use a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Patch the database path to use temp directory
            with patch('config.DATABASE_FOLDER', temp_dir):
                with patch('config.DATABASE_FILENAME', 'test.db'):
                    db = DatabaseManager()
                    
                    # Test adding a note
                    note_id = db.add_note("Test note content")
                    print(f"✓ Note added with ID: {note_id}")
                    
                    # Test getting all notes
                    notes = db.get_all_notes()
                    assert len(notes) == 1
                    assert notes[0]['content'] == "Test note content"
                    print("✓ Note retrieval successful")
                    
                    # Test updating a note
                    success = db.update_note(note_id, "Updated content")
                    assert success
                    print("✓ Note update successful")
                    
                    # Test getting specific note
                    note = db.get_note_by_id(note_id)
                    assert note['content'] == "Updated content"
                    print("✓ Specific note retrieval successful")
                    
                    # Test deleting a note
                    success = db.delete_note(note_id)
                    assert success
                    print("✓ Note deletion successful")
                    
                    # Verify note is deleted
                    notes = db.get_all_notes()
                    assert len(notes) == 0
                    print("✓ Note deletion verified")
                    
        print("✓ Database tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_clipboard_manager():
    """Test clipboard manager operations."""
    print("\nTesting clipboard manager...")
    
    try:
        # Test with mock clipboard to avoid system dependencies
        with patch('pyperclip.paste') as mock_paste:
            with patch('pyperclip.copy') as mock_copy:
                clip_manager = ClipboardManager(max_history=3)
                
                # Test adding items to history
                clip_manager._add_to_history("Item 1")
                clip_manager._add_to_history("Item 2")
                clip_manager._add_to_history("Item 3")
                
                history = clip_manager.get_clipboard_history()
                assert len(history) == 3
                assert history[0] == "Item 3"  # Most recent first
                print("✓ Clipboard history management successful")
                
                # Test history size limit
                clip_manager._add_to_history("Item 4")
                history = clip_manager.get_clipboard_history()
                assert len(history) == 3
                assert "Item 1" not in history
                print("✓ Clipboard history size limit working")
                
                # Test duplicate handling
                clip_manager._add_to_history("Item 3")
                history = clip_manager.get_clipboard_history()
                assert len(history) == 3
                assert history[0] == "Item 3"
                print("✓ Duplicate handling working")
                
                # Test clearing history
                clip_manager.clear_history()
                history = clip_manager.get_clipboard_history()
                assert len(history) == 0
                print("✓ Clear history working")
                
        print("✓ Clipboard manager tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Clipboard manager test failed: {e}")
        return False

def test_hotkey_manager():
    """Test hotkey manager operations."""
    print("\nTesting hotkey manager...")
    
    try:
        # Test with mock keyboard to avoid system dependencies
        with patch('keyboard.add_hotkey') as mock_add:
            with patch('keyboard.remove_hotkey') as mock_remove:
                hotkey_manager = HotkeyManager()
                
                # Test registering hotkey
                callback = Mock()
                hotkey_manager.register_hotkey("ctrl+alt+t", callback, "Test hotkey")
                
                registered = hotkey_manager.get_registered_hotkeys()
                assert "ctrl+alt+t" in registered
                print("✓ Hotkey registration successful")
                
                # Test unregistering hotkey
                hotkey_manager.unregister_hotkey("ctrl+alt+t")
                registered = hotkey_manager.get_registered_hotkeys()
                assert "ctrl+alt+t" not in registered
                print("✓ Hotkey unregistration successful")
                
        print("✓ Hotkey manager tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Hotkey manager test failed: {e}")
        return False

def test_config():
    """Test configuration module."""
    print("\nTesting configuration...")
    
    try:
        import config
        
        # Test config validation
        errors = config.validate_config()
        if errors:
            print(f"Configuration errors: {errors}")
        else:
            print("✓ Configuration validation passed")
        
        # Test config values
        assert config.CLIPBOARD_HISTORY_SIZE > 0
        assert config.DASHBOARD_WIDTH > 0
        assert config.DASHBOARD_HEIGHT > 0
        print("✓ Configuration values valid")
        
        # Test config summary
        summary = config.get_config_summary()
        assert "Configuration" in summary
        print("✓ Configuration summary generation successful")
        
        print("✓ Configuration tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Configuration test failed: {e}")
        return False

def test_hotkeys():
    """Test function to verify hotkey functionality."""
    print("Testing hotkey functionality...")
    
    # Initialize hotkey manager
    hotkey_manager = HotkeyManager()
    
    # Test callback function
    def test_callback():
        print("Hotkey callback triggered!")
    
    # Test the hotkeys from config
    print(f"Testing hotkey: {config.HOTKEY_TOGGLE_DASHBOARD}")
    is_valid = hotkey_manager.test_hotkey(config.HOTKEY_TOGGLE_DASHBOARD)
    print(f"Hotkey '{config.HOTKEY_TOGGLE_DASHBOARD}' is valid: {is_valid}")
    
    print(f"Testing hotkey: {config.HOTKEY_SAVE_NOTE}")
    is_valid = hotkey_manager.test_hotkey(config.HOTKEY_SAVE_NOTE)
    print(f"Hotkey '{config.HOTKEY_SAVE_NOTE}' is valid: {is_valid}")
    
    # Register and test a hotkey
    print("Registering test hotkey...")
    hotkey_manager.register_hotkey("ctrl+alt+t", test_callback, "Test hotkey")
    
    # Start monitoring
    print("Starting hotkey monitoring...")
    hotkey_manager.start_monitoring()
    
    print("Hotkeys registered:")
    for hotkey, description in hotkey_manager.get_registered_hotkeys().items():
        print(f"  {hotkey}: {description}")
    
    print("\nPress Ctrl+Alt+T within the next 10 seconds to test...")
    print("If the callback message appears, hotkeys are working correctly.")
    print("If not, there might be an issue with the hotkey registration.")
    
    # Wait for 10 seconds to allow manual testing
    for i in range(10, 0, -1):
        print(f"Time remaining: {i} seconds...", end="\r")
        time.sleep(1)
    
    print("\nTest completed. Stopping hotkey monitoring...")
    hotkey_manager.stop_monitoring()


def run_all_tests():
    """Run all tests."""
    print("QuickSave & Notes - Application Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_config,
        test_database,
        test_clipboard_manager,
        test_hotkey_manager
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! The application should work correctly.")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        
    return failed == 0

if __name__ == "__main__":
    # Check if we should run the hotkey test
    if len(sys.argv) > 1 and sys.argv[1] == "--test-hotkeys":
        test_hotkeys()
    else:
        # Run the unittest tests
        unittest.main() 