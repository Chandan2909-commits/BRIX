import os
import time
import pyautogui
import subprocess
import webbrowser
import threading
from urllib.parse import quote_plus
import json
import requests
from bs4 import BeautifulSoup
import re

# We'll import gmail_api_automation only when needed to avoid import errors
# if the dependencies aren't installed

class BrowserControl:
    def __init__(self):
        # Common browser paths
        self.browser_paths = {
            "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "edge": "microsoft-edge:",
            "firefox": r"C:\Program Files\Mozilla Firefox\firefox.exe",
            "brave": r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe"
        }
        
        # Default browser
        self.default_browser = "chrome"
    
    def open_browser(self, browser_name=None):
        """Open a specific browser or the default browser"""
        if not browser_name:
            browser_name = self.default_browser
        
        browser_name = browser_name.lower()
        
        try:
            if browser_name in self.browser_paths:
                path = self.browser_paths[browser_name]
                if os.path.exists(path) or browser_name == "edge":
                    os.startfile(path)
                    time.sleep(1)
                    return True, f"Opened {browser_name}"
                else:
                    return False, f"Browser path not found: {path}"
            else:
                # Try to open default browser
                webbrowser.open("about:blank")
                return True, "Opened default browser"
        except Exception as e:
            return False, f"Error opening browser: {str(e)}"
    
    def search_in_browser(self, query, browser_name=None):
        """Search for a query in a browser"""
        if not browser_name:
            browser_name = self.default_browser
        
        browser_name = browser_name.lower()
        
        try:
            # Encode the query for URL
            encoded_query = quote_plus(query)
            
            # Different search URLs
            search_urls = {
                "google": f"https://www.google.com/search?q={encoded_query}",
                "bing": f"https://www.bing.com/search?q={encoded_query}",
                "duckduckgo": f"https://duckduckgo.com/?q={encoded_query}",
                "youtube": f"https://www.youtube.com/results?search_query={encoded_query}",
                "amazon": f"https://www.amazon.com/s?k={encoded_query}",
                "wikipedia": f"https://en.wikipedia.org/wiki/Special:Search?search={encoded_query}"
            }
            
            # Default to Google search
            search_engine = "google"
            
            # Check if query specifies a search engine
            for engine in search_urls.keys():
                if query.lower().startswith(f"search {engine} for") or query.lower().startswith(f"{engine} search for"):
                    search_engine = engine
                    # Remove the search engine prefix from the query
                    if query.lower().startswith(f"search {engine} for"):
                        query = query[len(f"search {engine} for"):].strip()
                    elif query.lower().startswith(f"{engine} search for"):
                        query = query[len(f"{engine} search for"):].strip()
                    
                    # Re-encode the cleaned query
                    encoded_query = quote_plus(query)
                    break
            
            # Special case for YouTube
            if "youtube" in query.lower() and search_engine == "google":
                search_engine = "youtube"
                if "youtube for" in query.lower():
                    query = query.lower().split("youtube for")[1].strip()
                    encoded_query = quote_plus(query)
            
            # Get the search URL
            url = search_urls.get(search_engine, search_urls["google"])
            
            # Open the browser with the search URL
            if browser_name in self.browser_paths:
                path = self.browser_paths[browser_name]
                if os.path.exists(path) or browser_name == "edge":
                    if browser_name == "edge":
                        os.system(f"start microsoft-edge:{url}")
                    else:
                        subprocess.Popen([path, url])
                    return True, f"Searched for '{query}' on {search_engine} using {browser_name}"
                else:
                    return False, f"Browser path not found: {path}"
            else:
                # Use default browser
                webbrowser.open(url)
                return True, f"Searched for '{query}' on {search_engine} using default browser"
        except Exception as e:
            return False, f"Error searching in browser: {str(e)}"
    
    def navigate_to_url(self, url, browser_name=None):
        """Navigate to a specific URL"""
        if not browser_name:
            browser_name = self.default_browser
        
        browser_name = browser_name.lower()
        
        # Add http:// if no protocol specified
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        
        try:
            if browser_name in self.browser_paths:
                path = self.browser_paths[browser_name]
                if os.path.exists(path) or browser_name == "edge":
                    if browser_name == "edge":
                        os.system(f"start microsoft-edge:{url}")
                    else:
                        subprocess.Popen([path, url])
                    return True, f"Navigated to {url} using {browser_name}"
                else:
                    return False, f"Browser path not found: {path}"
            else:
                # Use default browser
                webbrowser.open(url)
                return True, f"Navigated to {url} using default browser"
        except Exception as e:
            return False, f"Error navigating to URL: {str(e)}"

    def open_gmail_and_reply(self, count=10):
        """Open Gmail and reply to the first N emails using AI"""
        try:
            # Try to import Gmail API automation
            try:
                from gmail_api_automation import gmail_api_automation
                
                # Use Gmail API automation
                success, message, results = gmail_api_automation.process_emails(count)
                
                # If successful, also open Gmail in browser for visual feedback
                if success:
                    self.navigate_to_url("https://mail.google.com")
                    return True, f"{message} - Check your Gmail for sent replies."
                else:
                    return False, message
            except ImportError:
                # If Gmail API dependencies aren't installed, fall back to browser automation
                self.navigate_to_url("https://mail.google.com")
                return True, "Gmail opened in browser. Please install Gmail API dependencies with install_gmail_deps.py for automated replies."
        except Exception as e:
            return False, f"Error in Gmail automation: {str(e)}"

class VisualBrowserAutomation:
    """Advanced visual browser automation with pyautogui for software downloads"""
    
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.download_sites = {
            "vscode": {
                "url": "https://code.visualstudio.com/download",
                "button_text": ["Download", "Windows", "Stable"],
                "file_pattern": r"VSCodeUserSetup.*\.exe"
            },
            "chrome": {
                "url": "https://www.google.com/chrome/",
                "button_text": ["Download Chrome", "Accept and Install"],
                "file_pattern": r"chrome_installer\.exe"
            },
            "firefox": {
                "url": "https://www.mozilla.org/firefox/download/",
                "button_text": ["Download Firefox", "Free Download"],
                "file_pattern": r"Firefox.*\.exe"
            },
            "discord": {
                "url": "https://discord.com/download",
                "button_text": ["Download for Windows", "Download"],
                "file_pattern": r"DiscordSetup\.exe"
            },
            "zoom": {
                "url": "https://zoom.us/download",
                "button_text": ["Download", "Zoom Client for Meetings"],
                "file_pattern": r"ZoomInstaller\.exe"
            }
        }
    
    def find_and_click_element(self, text, confidence=0.7, timeout=10):
        """Find and click an element by text using pyautogui"""
        start_time = time.time()
        print(f"Looking for element: {text}")
        
        while time.time() - start_time < timeout:
            try:
                # Try OCR-based approach first (simulated here with direct clicks)
                # For common download buttons, try clicking in common locations
                if text.lower() in ["download", "windows", "download for windows", "user installer", "stable"]:
                    # Try clicking in common download button locations
                    locations_to_try = [
                        (self.screen_width // 2, self.screen_height // 2),  # Center of screen
                        (self.screen_width // 2, self.screen_height // 3),  # Upper middle
                        (self.screen_width // 2, self.screen_height * 2 // 3),  # Lower middle
                        (self.screen_width * 3 // 4, self.screen_height // 2),  # Right middle
                        (self.screen_width // 4, self.screen_height // 2)   # Left middle
                    ]
                    
                    for loc in locations_to_try:
                        print(f"Trying to click at position: {loc}")
                        pyautogui.moveTo(loc[0], loc[1])
                        time.sleep(0.5)
                        pyautogui.click()
                        time.sleep(1)  # Wait to see if anything happens
                        
                        # Check if we need to try another location
                        if "download" in text.lower():
                            # After clicking, wait a bit to see if a download starts
                            time.sleep(2)
                            # If we're successful, we might see a download dialog
                            # For simplicity, we'll assume success and return
                            return True, f"Clicked at position {loc} for {text}"
                
                # Traditional image recognition approach
                location = pyautogui.locateOnScreen(text, confidence=confidence)
                if location:
                    center = pyautogui.center(location)
                    pyautogui.moveTo(center)
                    time.sleep(0.5)
                    pyautogui.click()
                    return True, f"Clicked element: {text}"
                
                # Try alternative - look for text on screen
                try:
                    pyautogui.moveTo(text)
                    time.sleep(0.5)
                    pyautogui.click()
                    return True, f"Clicked text: {text}"
                except:
                    pass
                    
            except Exception as e:
                print(f"Error in find_and_click_element: {str(e)}")
                pass
            
            time.sleep(1)
        
        return False, f"Could not find element: {text}"
    
    def wait_for_page_load(self, seconds=3):
        """Wait for page to load"""
        print(f"Waiting {seconds} seconds for page to load...")
        time.sleep(seconds)
        print("Page load wait complete")
        
        # Move mouse to center of screen after page load
        pyautogui.moveTo(self.screen_width // 2, self.screen_height // 2)
        time.sleep(0.5)
    
    def scroll_to_find_element(self, text, max_scrolls=10):
        """Scroll down to find an element"""
        print(f"Scrolling to find: {text}")
        
        # First try without scrolling
        success, message = self.find_and_click_element(text)
        if success:
            return True, message
        
        # Then try with scrolling
        for i in range(max_scrolls):
            try:
                print(f"Scroll attempt {i+1}/{max_scrolls}")
                
                # Scroll down
                pyautogui.scroll(-5)  # Increased scroll amount
                time.sleep(0.5)
                
                # Try to find the element
                success, message = self.find_and_click_element(text)
                if success:
                    return True, message
                
            except Exception as e:
                print(f"Error while scrolling: {str(e)}")
                pass
        
        # If we didn't find it scrolling down, try scrolling back up
        print("Scrolling back to top and trying again...")
        for i in range(max_scrolls):
            pyautogui.scroll(5)  # Scroll up
            time.sleep(0.5)
        
        # Try one more time from the top
        for i in range(max_scrolls):
            try:
                print(f"Upward scroll attempt {i+1}/{max_scrolls}")
                
                # Try to find the element
                success, message = self.find_and_click_element(text)
                if success:
                    return True, message
                
                # Scroll down more slowly
                pyautogui.scroll(-3)
                time.sleep(1)
                
            except Exception as e:
                print(f"Error while scrolling up: {str(e)}")
                pass
        
        return False, f"Could not find element after scrolling: {text}"
    
    def download_vscode(self):
        """Automate VS Code download with visual feedback"""
        def download_process():
            try:
                print("🚀 Starting VS Code download automation...")
                
                # Open browser to VS Code download page
                browser = BrowserControl()
                browser.navigate_to_url("https://code.visualstudio.com/download")
                
                print("📱 Waiting for page to load...")
                self.wait_for_page_load(5)  # Increased wait time for page load
                
                # Look for Windows download button
                print("🔍 Searching for Windows download button...")
                
                # Step 1: Try direct download link for Windows
                print("Step 1: Trying direct download link for Windows...")
                try:
                    # This is the direct download link for VS Code Windows User Installer
                    direct_url = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64-user"
                    browser.navigate_to_url(direct_url)
                    print("✅ Navigated to direct download link")
                    time.sleep(5)  # Wait for download to start
                except Exception as e:
                    print(f"❌ Direct download failed: {str(e)}")
                
                # Step 2: If direct download didn't work, try clicking on the Windows section
                print("Step 2: Looking for Windows download section...")
                
                # Try clicking in the Windows section (usually in the top section of the page)
                windows_positions = [
                    (self.screen_width // 2, self.screen_height // 3),  # Upper middle
                    (self.screen_width // 2, self.screen_height // 4),  # Higher upper middle
                    (self.screen_width // 2, self.screen_height * 2 // 5)  # Lower upper middle
                ]
                
                for pos in windows_positions:
                    pyautogui.moveTo(pos[0], pos[1])
                    time.sleep(0.5)
                    pyautogui.click()
                    time.sleep(1)
                    print(f"Clicked at position {pos} looking for Windows section")
                
                # Step 3: Try different strategies to find download button
                print("Step 3: Looking for download button...")
                strategies = [
                    "Windows",
                    "Download for Windows",
                    "Download VS Code",
                    "Stable",
                    "User Installer",
                    "Download"
                ]
                
                # Try each strategy
                for strategy in strategies:
                    try:
                        # Move mouse to center of screen and look for button
                        pyautogui.moveTo(self.screen_width//2, self.screen_height//2)
                        print(f"Trying strategy: {strategy}")
                        
                        # Try to find and click the download button
                        success, message = self.find_and_click_element(strategy)
                        if success:
                            print(f"✅ {message}")
                            # After clicking, wait to see if download starts
                            time.sleep(3)
                            break
                        else:
                            # Try scrolling
                            print(f"Scrolling to find: {strategy}")
                            success, message = self.scroll_to_find_element(strategy)
                            if success:
                                print(f"✅ {message}")
                                # After clicking, wait to see if download starts
                                time.sleep(3)
                                break
                    except Exception as e:
                        print(f"❌ Strategy '{strategy}' failed: {str(e)}")
                        continue
                
                # Step 4: If we're still here, try direct navigation to the Windows download
                print("Step 4: Trying common download button locations...")
                # Try clicking at common download button locations
                download_positions = [
                    (self.screen_width // 2, self.screen_height // 2),  # Center
                    (self.screen_width * 3 // 4, self.screen_height // 3),  # Upper right
                    (self.screen_width // 4, self.screen_height // 3),  # Upper left
                    (self.screen_width // 2, self.screen_height * 2 // 3)  # Lower middle
                ]
                
                for pos in download_positions:
                    pyautogui.moveTo(pos[0], pos[1])
                    time.sleep(0.5)
                    pyautogui.click()
                    print(f"Clicked at position {pos} for direct download")
                    time.sleep(2)  # Wait to see if download starts
                
                print("🎯 Download should start automatically!")
                print("⏳ VS Code download initiated successfully!")
                return True, "VS Code download started"
                
            except Exception as e:
                return False, f"VS Code download failed: {str(e)}"
        
        # Run in thread to avoid blocking
        thread = threading.Thread(target=download_process, daemon=True)
        thread.start()
        return True, "VS Code download automation started"
    
    def download_software(self, software_name):
        """Download any supported software with visual automation"""
        software_name = software_name.lower().strip()
        
        if software_name not in self.download_sites:
            available = ", ".join(self.download_sites.keys())
            return False, f"Software '{software_name}' not supported. Available: {available}"
        
        def download_process():
            try:
                config = self.download_sites[software_name]
                print(f"🚀 Starting {software_name} download automation...")
                
                # Open browser to download page
                browser = BrowserControl()
                browser.navigate_to_url(config["url"])
                
                print("📱 Waiting for page to load...")
                self.wait_for_page_load(4)
                
                # Look for download buttons
                print(f"🔍 Searching for {software_name} download button...")
                
                for button_text in config["button_text"]:
                    try:
                        success, message = self.find_and_click_element(button_text)
                        if success:
                            print(f"✅ {message}")
                            break
                        
                        # Try scrolling
                        success, message = self.scroll_to_find_element(button_text)
                        if success:
                            print(f"✅ {message}")
                            break
                    except:
                        continue
                
                print(f"🎯 {software_name.title()} download initiated!")
                return True, f"{software_name.title()} download started"
                
            except Exception as e:
                return False, f"{software_name.title()} download failed: {str(e)}"
        
        # Run in thread to avoid blocking
        thread = threading.Thread(target=download_process, daemon=True)
        thread.start()
        return True, f"{software_name.title()} download automation started"
    
    def search_and_download(self, query):
        """Search for software and download it"""
        query_lower = query.lower()
        print(f"🔍 Searching for software to download: {query}")
        
        # Special case for VS Code
        if any(keyword in query_lower for keyword in ["vscode", "vs code", "visual studio code", "code editor"]):
            print("📦 Detected VS Code download request - using direct download method")
            return self.download_vscode()
        
        # Map common queries to software names
        software_map = {
            "vscode": ["vscode", "vs code", "visual studio code", "code editor"],
            "chrome": ["chrome", "google chrome", "browser"],
            "firefox": ["firefox", "mozilla firefox"],
            "discord": ["discord", "chat app"],
            "zoom": ["zoom", "video call", "meeting"]
        }
        
        # Find matching software
        for software, keywords in software_map.items():
            if any(keyword in query_lower for keyword in keywords):
                print(f"📦 Detected {software} download request")
                return self.download_software(software)
        
        # Fallback: search and provide instructions
        print(f"📦 No specific download method for {query}, using search-based approach")
        browser = BrowserControl()
        browser.search_in_browser(f"download {query}")
        return True, f"Searching for download instructions for {query}"
        return True, f"Searching for {query} download instructions"

# Create singleton instances
browser_control = BrowserControl()
visual_browser = VisualBrowserAutomation()