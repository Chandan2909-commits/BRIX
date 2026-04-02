import os
import sys
import base64
import json
import time
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Define scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Credentials file path
CREDENTIALS_FILE = 'credentials.json'
TOKEN_FILE = 'gmail_token.json'  # Using a different name to avoid conflicts

def get_service():
    """Get Gmail API service."""
    creds = None
    
    # Check if token file exists
    if os.path.exists(TOKEN_FILE):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        except Exception as e:
            print(f"Error loading token: {e}")
    
    # If no valid credentials, authenticate
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                print(f"Error refreshing token: {e}")
                creds = None
        
        # If still no valid creds, do OAuth flow
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                print(f"Error: {CREDENTIALS_FILE} not found!")
                return None
            
            try:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
                creds = flow.run_local_server(port=0)
                
                # Save token
                try:
                    with open(TOKEN_FILE, 'w') as token:
                        token.write(creds.to_json())
                    print(f"Token saved to {TOKEN_FILE}")
                except Exception as e:
                    print(f"Error saving token: {e}")
            except Exception as e:
                print(f"Authentication error: {e}")
                return None
    
    # Build service
    try:
        service = build('gmail', 'v1', credentials=creds)
        return service
    except Exception as e:
        print(f"Error building service: {e}")
        return None

def get_unread_messages(service, max_results=10):
    """Get unread messages from inbox."""
    try:
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q='is:unread',
            maxResults=max_results
        ).execute()
        
        messages = results.get('messages', [])
        return messages
    except Exception as e:
        print(f"Error getting messages: {e}")
        return []

def get_message_details(service, msg_id):
    """Get message details."""
    try:
        msg = service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        
        # Extract headers
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
        
        # Extract content
        content = ""
        if 'parts' in msg['payload']:
            for part in msg['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    content = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    break
        elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
            content = base64.urlsafe_b64decode(msg['payload']['body']['data']).decode('utf-8')
        
        return {
            'id': msg_id,
            'threadId': msg['threadId'],
            'subject': subject,
            'sender': sender,
            'content': content
        }
    except Exception as e:
        print(f"Error getting message details: {e}")
        return None

def extract_email(sender):
    """Extract email from sender string."""
    if '<' in sender and '>' in sender:
        return sender.split('<')[1].split('>')[0]
    return sender

def send_reply(service, thread_id, to_email, subject, body):
    """Send reply to email."""
    try:
        message = MIMEText(body)
        message['to'] = to_email
        message['subject'] = f"Re: {subject}"
        
        raw = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        body = {
            'raw': raw,
            'threadId': thread_id
        }
        
        sent = service.users().messages().send(userId='me', body=body).execute()
        return sent
    except Exception as e:
        print(f"Error sending reply: {e}")
        return None

def mark_as_read(service, msg_id):
    """Mark message as read."""
    try:
        service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
        return True
    except Exception as e:
        print(f"Error marking as read: {e}")
        return False

def main():
    """Main function."""
    # Get max results from command line
    max_results = 10
    if len(sys.argv) > 1:
        try:
            max_results = int(sys.argv[1])
        except:
            pass
    
    print(f"\n=== Gmail Auto-Reply (Processing {max_results} messages) ===\n")
    
    # Get service
    service = get_service()
    if not service:
        print("Failed to initialize Gmail API.")
        return
    
    # Get unread messages
    print("Fetching unread messages...")
    messages = get_unread_messages(service, max_results)
    
    if not messages:
        print("No unread messages found.")
        return
    
    print(f"Found {len(messages)} unread messages.")
    
    # Process messages
    for i, message in enumerate(messages):
        print(f"\nProcessing message {i+1}/{len(messages)}")
        
        # Get message details
        msg_details = get_message_details(service, message['id'])
        if not msg_details:
            print("Failed to get message details. Skipping.")
            continue
        
        print(f"Subject: {msg_details['subject']}")
        print(f"From: {msg_details['sender']}")
        
        # Generate reply
        reply = "Thank you for your email. I've received your message and will respond properly soon. This is an automated acknowledgment."
        
        # Send reply
        to_email = extract_email(msg_details['sender'])
        print(f"Sending reply to {to_email}...")
        
        sent = send_reply(
            service,
            msg_details['threadId'],
            to_email,
            msg_details['subject'],
            reply
        )
        
        if sent:
            print("Reply sent successfully.")
            
            # Mark as read
            if mark_as_read(service, message['id']):
                print("Marked as read.")
            else:
                print("Failed to mark as read.")
        else:
            print("Failed to send reply.")
    
    print("\n=== Processing completed ===")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nPress Enter to exit...")
    input()