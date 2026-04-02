import time
import os
from browser_control import browser_control
from system_settings import system_settings

def test_browser_chain():
    """Test a chain of browser actions"""
    print("Testing browser chain...")
    
    # Step 1: Open Chrome
    print("Step 1: Opening Chrome...")
    success, message = browser_control.open_browser("chrome")
    print(message)
    time.sleep(2)  # Wait for Chrome to open
    
    # Step 2: Search for something on YouTube
    print("Step 2: Searching YouTube...")
    success, message = browser_control.search_in_browser("youtube for cats", "chrome")
    print(message)
    time.sleep(3)  # Wait for search results
    
    # Step 3: Adjust brightness
    print("Step 3: Adjusting brightness...")
    success, message = system_settings.adjust_brightness(level=70)
    print(message)
    time.sleep(2)
    
    # Step 4: Adjust volume
    print("Step 4: Adjusting volume...")
    success, message = system_settings.adjust_volume(level=50)
    print(message)
    time.sleep(2)
    
    print("Test completed!")

if __name__ == "__main__":
    # Wait 3 seconds before starting to give time to switch to the right window
    print("Test will start in 3 seconds. Switch to the appropriate window if needed.")
    time.sleep(3)
    
    test_browser_chain()