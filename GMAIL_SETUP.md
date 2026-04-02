# Gmail Automation Setup

This script automates reading and replying to unread Gmail messages using the Gmail API and a local LLM (Ollama).

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable the Gmail API for your project
4. Create OAuth 2.0 credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as the application type
   - Name your client and click "Create"
5. Download the credentials JSON file
6. Rename it to `credentials.json` and place it in the same directory as the script

### 3. Set Up Ollama (Local LLM)

1. Install Ollama from [https://ollama.ai/](https://ollama.ai/)
2. Pull the Mistral model:
   ```bash
   ollama pull mistral
   ```

## Running the Script

```bash
python gmail_automation.py
```

The first time you run the script, it will open a browser window for you to authenticate with your Google account. After authentication, a `token.json` file will be created to store your credentials for future runs.

## What the Script Does

1. Authenticates with the Gmail API
2. Fetches up to 20 unread messages from your inbox
3. For each message:
   - Extracts the sender, subject, and content
   - Generates a reply using the local LLM (Ollama)
   - Sends the reply
   - Marks the original message as read

## Troubleshooting

- If you encounter authentication issues, delete the `token.json` file and run the script again
- Make sure the Ollama service is running before executing the script
- Check that your Google account has not blocked the app due to security settings