import json
import time
import pyautogui
import os

def test_simple_chain():
    """Test a simple chain of events: open notepad, write text, save file"""
    print("Testing simple chain of events...")
    
    # Step 1: Open Notepad
    print("Step 1: Opening Notepad...")
    os.startfile("notepad.exe")
    time.sleep(2)  # Wait for Notepad to open
    
    # Step 2: Write text
    print("Step 2: Writing text...")
    pyautogui.typewrite("This is a test of the Chain of Events functionality in BRIX.")
    time.sleep(1)
    
    # Step 3: Save file
    print("Step 3: Saving file...")
    pyautogui.hotkey('ctrl', 's')
    time.sleep(1)
    
    # Type the path to save
    save_path = os.path.join(os.path.expanduser("~"), "Downloads", "brix_test.txt")
    pyautogui.typewrite(save_path)
    time.sleep(1)
    
    # Press Enter to save
    pyautogui.press('enter')
    time.sleep(1)
    
    # Handle potential overwrite confirmation
    try:
        pyautogui.press('y')
    except:
        pass
    
    print("Test completed!")
    print(f"File saved to: {save_path}")

if __name__ == "__main__":
    # Wait 3 seconds before starting to give time to switch to the right window
    print("Test will start in 3 seconds. Switch to the appropriate window if needed.")
    time.sleep(3)
    
    test_simple_chain()