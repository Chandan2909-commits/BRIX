import os
import subprocess
import time
import pyautogui

class SystemSettings:
    def __init__(self):
        pass
    
    def adjust_brightness(self, level=None, change=None):
        """
        Adjust screen brightness
        level: absolute brightness level (0-100)
        change: relative brightness change (+10, -20, etc.)
        """
        try:
            # Use PowerShell to adjust brightness
            if level is not None:
                # Ensure level is within range
                level = max(0, min(100, level))
                
                # PowerShell command to set brightness
                cmd = f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{level})"
                subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True, f"Brightness set to {level}%"
            
            elif change is not None:
                # Get current brightness using PowerShell
                get_cmd = "powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightness).CurrentBrightness"
                result = subprocess.run(get_cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                
                try:
                    current = int(result.stdout.strip())
                    new_level = max(0, min(100, current + change))
                    
                    # Set new brightness
                    set_cmd = f"powershell (Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1,{new_level})"
                    subprocess.run(set_cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                    return True, f"Brightness changed from {current}% to {new_level}%"
                except:
                    # Fall back to keyboard simulation if PowerShell fails
                    if change > 0:
                        steps = abs(change) // 10
                        for _ in range(steps):
                            pyautogui.hotkey('fn', 'f3')  # Increase brightness
                            time.sleep(0.1)
                    else:
                        steps = abs(change) // 10
                        for _ in range(steps):
                            pyautogui.hotkey('fn', 'f2')  # Decrease brightness
                            time.sleep(0.1)
                    
                    return True, f"Brightness changed by approximately {change}%"
            
            return False, "No brightness level or change specified"
        except Exception as e:
            return False, f"Error adjusting brightness: {str(e)}"
    
    def adjust_volume(self, level=None, change=None, mute=None):
        """
        Adjust system volume
        level: absolute volume level (0-100)
        change: relative volume change (+10, -20, etc.)
        mute: True to mute, False to unmute
        """
        try:
            # Handle mute/unmute
            if mute is not None:
                pyautogui.press('volumemute')
                return True, "Volume muted" if mute else "Volume unmuted"
            
            # Handle absolute volume level
            if level is not None:
                # Use PowerShell to set volume
                cmd = f'powershell -c "(New-Object -ComObject WScript.Shell).SendKeys(\'[{{{level}}}\');"'
                subprocess.run(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                return True, f"Volume set to {level}%"
            
            # Handle relative volume change
            elif change is not None:
                # Each press is ~2%
                steps = abs(change) // 2
                
                if change > 0:
                    for _ in range(steps):
                        pyautogui.press('volumeup')
                        time.sleep(0.02)
                else:
                    for _ in range(steps):
                        pyautogui.press('volumedown')
                        time.sleep(0.02)
                
                return True, f"Volume changed by {change}%"
            
            return False, "No volume level, change, or mute/unmute specified"
        except Exception as e:
            return False, f"Error adjusting volume: {str(e)}"
    
    def toggle_wifi(self, enable=None):
        """Toggle WiFi on or off"""
        try:
            if enable is None:
                # Toggle current state
                pyautogui.hotkey('win', 'a')  # Open action center
                time.sleep(0.5)
                
                # Click on WiFi icon (position may vary)
                # This is approximate and may need adjustment
                pyautogui.click(x=1000, y=500)
                
                # Close action center
                pyautogui.press('escape')
                return True, "WiFi toggled"
            
            # Use netsh to enable/disable WiFi
            if enable:
                subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "enabled"], 
                              creationflags=subprocess.CREATE_NO_WINDOW)
                return True, "WiFi enabled"
            else:
                subprocess.run(["netsh", "interface", "set", "interface", "Wi-Fi", "disabled"], 
                              creationflags=subprocess.CREATE_NO_WINDOW)
                return True, "WiFi disabled"
        except Exception as e:
            return False, f"Error toggling WiFi: {str(e)}"

# Create a singleton instance
system_settings = SystemSettings()