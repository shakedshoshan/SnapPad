import keyboard
import time
import sys

def on_hotkey():
    print("Hotkey pressed!")

def main():
    print("Testing keyboard library...")
    print("Registering hotkey: ctrl+alt+t")
    
    try:
        keyboard.add_hotkey('ctrl+alt+t', on_hotkey)
        print("Hotkey registered successfully")
        print("Press Ctrl+Alt+T to test the hotkey...")
        print("Press Ctrl+C to exit")
        
        # Keep the script running
        while True:
            time.sleep(1)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        keyboard.unhook_all()

if __name__ == "__main__":
    main() 