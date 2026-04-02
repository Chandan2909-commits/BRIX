# Gmail API Setup for BRIX

This document explains how to set up the Gmail API for BRIX to automatically reply to emails.

## Step 1: Install Dependencies

Run one of the following:

- **Windows**: Double-click `install_gmail_deps.bat`
- **Any OS**: Run `python install_gmail_deps.py`

This will install the required Google API packages:
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib

## Step 2: Set Up Gmail API Credentials

1. Run `python setup_gmail_api.py` and follow the instructions
2. When prompted, enter your client secret

## Step 3: Use the Gmail Automation

Use one of these commands in BRIX:
- `open gmail and reply to first 10 messages`
- `open gmail and reply to first 20 messages`

Or click one of these quick command buttons:
- "Gmail Auto-Reply"
- "Gmail Reply 20"

## Step 4: Direct Command Line Usage

You can also run the Gmail automation directly from the command line:

```
python run_gmail_api.py
```

Or use the batch file for quick access:

```
gmail_reply.bat 10
```

Where 10 is the number of messages to process.

## Troubleshooting

If you encounter any issues:

1. Make sure the dependencies are installed
2. Check that your credentials.json file is set up correctly
3. Try running `python test_gmail_api.py` to test the Gmail API directly

### Access Denied Issues

If you're getting "Access Denied" errors, try these solutions in order:

#### Solution 1: Use Browser-Only Mode

If you just need to access Gmail quickly without API integration:

1. Double-click `GMAIL_BROWSER_ONLY.bat`
2. This will open Gmail in your browser without requiring API access

#### Solution 2: Try Direct Access Method

This method attempts to bypass permission issues:

1. Double-click `GMAIL_DIRECT_ACCESS.bat`
2. Follow the on-screen instructions
3. When prompted in the browser, make sure to click "Continue" and grant ALL permissions

#### Solution 3: Fix API Access

If you want to fix the API access properly:

1. Run the access fix utility:
   ```
   python fix_gmail_access.py
   ```

2. Make sure you've enabled the Gmail API in your Google Cloud Console:
   - Go to https://console.cloud.google.com/apis/library/gmail.googleapis.com
   - Click "Enable" if it's not already enabled

3. Add your email as a test user in OAuth consent screen settings:
   - Go to https://console.cloud.google.com/apis/credentials/consent
   - Add your email address under "Test users"

4. When prompted to allow access, click "Continue" and grant ALL requested permissions

5. If using a Google Workspace account, check with your administrator about API access restrictions