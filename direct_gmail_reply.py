import os
import sys
import base64
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

def get_credentials():
    """Get Gmail API credentials."""
    # Load credentials from credentials.json
    flow = InstalledAppFlow.from_client_secrets_file(
        'credentials.json',
        SCOPES
    )
    
    # Run local server for authentication
    print("Opening browser for authentication...")
    credentials = flow.run_local_server(port=0)
    
    return credentials

def process_emails(credentials, max_count=10):
    """Process unread emails."""
    try:
        # Build Gmail API service
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get unread messages
        print(f"Fetching up to {max_count} unread messages...")
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q='is:unread',
            maxResults=max_count
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            print("No unread messages found.")
            return 0, 0
        
        print(f"Found {len(messages)} unread messages.")
        
        success_count = 0
        error_count = 0
        
        # Process each message
        for i, message in enumerate(messages):
            try:
                # Get message details
                msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
                
                # Extract headers
                headers = msg['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'].lower() == 'subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'].lower() == 'from'), 'Unknown')
                
                # Extract email address
                to_email = sender
                if '<' in sender and '>' in sender:
                    to_email = sender.split('<')[1].split('>')[0]
                
                print(f"\nProcessing message {i+1}/{len(messages)}")
                print(f"Subject: {subject}")
                print(f"From: {sender}")
                
                # Create reply
                reply_text = "Thank you for your email. I've received your message and will respond properly soon. This is an automated acknowledgment."
                message_obj = MIMEText(reply_text)
                message_obj['to'] = to_email
                message_obj['subject'] = f"Re: {subject}"
                
                # Encode and send
                raw = base64.urlsafe_b64encode(message_obj.as_bytes()).decode('utf-8')
                body = {
                    'raw': raw,
                    'threadId': msg['threadId']
                }
                
                # Send reply
                service.users().messages().send(userId='me', body=body).execute()
                print(f"Reply sent to {to_email}")
                
                # Mark as read
                service.users().messages().modify(
                    userId='me',
                    id=message['id'],
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                print("Marked as read")
                
                success_count += 1
                
            except Exception as e:
                print(f"Error processing message: {e}")
                error_count += 1
        
        return success_count, error_count
        
    except HttpError as error:
        print(f"API error: {error}")
        return 0, 0
    except Exception as e:
        print(f"Error: {e}")
        return 0, 0

def main():
    """Main function."""
    # Get message count from command line
    message_count = 10
    if len(sys.argv) > 1:
        try:
            message_count = int(sys.argv[1])
        except:
            pass
    
    print("\n=== BRIX Gmail Auto-Reply ===\n")
    print(f"Will process up to {message_count} unread messages.\n")
    
    try:
        # Get credentials
        credentials = get_credentials()
        
        # Process emails
        success_count, error_count = process_emails(credentials, message_count)
        
        # Print summary
        print("\n=== Summary ===")
        print(f"Successfully processed: {success_count}")
        print(f"Errors: {error_count}")
        print("\nDone!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    print("\nPress Enter to exit...")
    input()

if __name__ == "__main__":
    main()