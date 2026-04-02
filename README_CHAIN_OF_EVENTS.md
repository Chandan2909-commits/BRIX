# Chain of Events in BRIX

This document explains how to use the Chain of Events functionality in BRIX, which allows you to execute multiple actions in sequence with a single command.

## Overview

Chain of Events allows you to:
- Execute multiple actions in sequence
- Automate common workflows
- Combine different types of actions (opening apps, writing text, saving files, sending messages)

## Supported Actions

The following actions are supported in chains:

### Basic Actions
1. `open_app`: Open an application
2. `write_text`: Type text using keyboard simulation
3. `save_file`: Save a file using keyboard shortcuts
4. `send_message`: Send a message via Telegram
5. `close_app`: Close an application
6. `list_files`: List files in a directory
7. `run_command`: Run a command in CMD or PowerShell
8. `search_files`: Search for files of a specific type
9. `wait`: Wait for a specified number of seconds

### Browser Actions
10. `open_browser`: Open a specific browser (Chrome, Edge, Firefox)
11. `search_web`: Search the web using a specific search engine
12. `navigate_to`: Navigate to a specific URL
13. `gmail_reply`: Open Gmail and automatically reply to emails using AI

### System Settings
13. `adjust_brightness`: Adjust screen brightness (absolute or relative)
14. `adjust_volume`: Adjust system volume (absolute or relative)
15. `toggle_wifi`: Toggle WiFi on or off

## Example Commands

Here are some example commands you can try:

### Basic Chains

1. **Simple Notepad Chain**:
   ```
   Open Notepad, write "Hello World", save as hello.txt in Downloads
   ```

2. **Telegram Message Chain**:
   ```
   Open Notepad, write "Meeting notes", save as notes.txt, then send to John on Telegram with message "Here are the meeting notes"
   ```

3. **File Management Chain**:
   ```
   List files in Downloads, open the newest PDF, then close it after 5 seconds
   ```

### Browser Chains

4. **Web Search Chain**:
   ```
   Open Chrome, search YouTube for cats, wait 5 seconds, close Chrome
   ```

5. **Multiple Searches Chain**:
   ```
   Open Chrome, search for weather forecast, wait 3 seconds, search YouTube for music
   ```

6. **Research Chain**:
   ```
   Open Edge, navigate to https://en.wikipedia.org, search for quantum computing, wait 10 seconds
   ```

7. **Gmail Auto-Reply Chain**:
   ```
   Open Gmail and reply to first 10 messages
   ```
   
8. **Gmail Custom Count Chain**:
   ```
   Open Gmail and reply to first 20 messages
   ```

9. **Gmail API Setup**:
   ```
   Setup Gmail API
   ```
   
10. **Gmail Calibration** (for browser automation fallback):
   ```
   Calibrate Gmail
   ```

### System Settings Chains

7. **Presentation Setup Chain**:
   ```
   Set brightness to 80%, set volume to 50%, open PowerPoint
   ```

8. **Night Mode Chain**:
   ```
   Set brightness to 30%, open Chrome, navigate to youtube.com/music
   ```

9. **Movie Setup Chain**:
   ```
   Open Chrome, search YouTube for movie trailers, set brightness to 70%, set volume to 90%
   ```

## Configuring Telegram

To use the Telegram functionality, you need to:

1. Create a Telegram bot using BotFather
2. Get your bot token
3. Update the `config.json` file with your bot token and contact chat IDs

### Getting Chat IDs

To get a chat ID:
1. Add your bot to a chat
2. Send a message to the bot
3. Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
4. Look for the `chat` object and note the `id` field

### Updating Configuration

You can update the configuration in two ways:

1. **Manually**: Edit the `config.json` file directly
2. **Programmatically**: Use the `configure_telegram` method in your code

## Safety Features

- Chains are limited to 5 steps by default (can be changed in code)
- Confirmation is required for chains with more than 5 steps
- Destructive actions (like file deletion) require confirmation

## Troubleshooting

- **UI Automation Issues**: If pyautogui fails to interact with applications, try increasing the delay between steps
- **Gmail API Issues**: Run the "Setup Gmail API" command and follow the instructions to set up Gmail API credentials
- **Gmail Browser Automation Issues**: If Gmail API doesn't work, run the "Calibrate Gmail" command to set up the correct screen coordinates for browser-based automation
- **Telegram Errors**: Make sure your bot token is correct and the bot has permission to send messages to the specified chat
- **Parsing Errors**: If the AI fails to parse your command correctly, try being more explicit in your instructions

## Testing

You can test the Chain of Events functionality using the provided `test_chain.py` script:

```
python test_chain.py
```

This will run a simple test that opens Notepad, writes text, and saves a file.


okay but i have a better idea ...since i have a power of llm in my back okay ....now i want na that in my browser i can open gmail and then reply to selected first messages like first 10 messages or 20 messages as the user suggest ...and then the ai agent can automatically opens gmail in chrome and then messages each of them using llm we can draft message automatically and then send them automatically ...understood what i am trying to achieve here