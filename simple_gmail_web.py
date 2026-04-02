import os
import sys
import base64
import pickle
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# Global variables
credentials = None
message_count = 10
flow_state = None
processed_count = 0
success_count = 0
error_count = 0

class GmailHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global credentials, message_count, flow_state, processed_count, success_count, error_count
        
        # Parse URL
        path = self.path
        query = {}
        if '?' in path:
            path, query_string = path.split('?', 1)
            query = urllib.parse.parse_qs(query_string)
        
        # Handle different paths
        if path == '/':
            # Main page - start authentication
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>BRIX Gmail Auto-Reply</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                    h1 { color: #0066cc; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .info { background-color: #d9edf7; color: #31708f; }
                    button { background-color: #0066cc; color: white; border: none; padding: 10px 15px; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>BRIX Gmail Auto-Reply</h1>
                    <div class="status info">
                        <p>Welcome to BRIX Gmail Auto-Reply</p>
                        <p>This tool will help you automatically reply to unread emails in your Gmail inbox.</p>
                    </div>
                    <p>Number of messages to process: <b>{}</b></p>
                    <p>Click the button below to authorize access to your Gmail account:</p>
                    <form action="/auth" method="get">
                        <button type="submit">Authorize Gmail Access</button>
                    </form>
                </div>
            </body>
            </html>
            """.format(message_count)
            
            self.wfile.write(html.encode())
            
        elif path == '/auth':
            global flow_state
            # Start OAuth flow
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json',
                scopes=SCOPES,
                redirect_uri='http://localhost:8080/oauth2callback'
            )
            
            # Store flow in global variable
            flow_state = flow
            
            # Get authorization URL
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true'
            )
            
            # Redirect to auth URL
            self.send_response(302)
            self.send_header('Location', auth_url)
            self.end_headers()
            
        elif path == '/oauth2callback':
            # Handle OAuth callback
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_start = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>BRIX Gmail Auto-Reply</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                    h1 { color: #0066cc; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .success { background-color: #dff0d8; color: #3c763d; }
                    .error { background-color: #f2dede; color: #a94442; }
                    button { background-color: #0066cc; color: white; border: none; padding: 10px 15px; cursor: pointer; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>BRIX Gmail Auto-Reply</h1>
            """
            
            html_end = """
                </div>
            </body>
            </html>
            """
            
            global flow_state
            try:
                # Get credentials from flow
                if not flow_state:
                    html = html_start
                    html += """
                        <div class="status error">
                            <p>Authentication failed: Session expired</p>
                        </div>
                        <p>Please try again:</p>
                        <form action="/auth" method="get">
                            <button type="submit">Retry Authorization</button>
                        </form>
                    """
                    html += html_end
                    self.wfile.write(html.encode())
                    return
                
                flow_state.fetch_token(authorization_response=self.path)
                credentials = flow_state.credentials
                
                html = html_start
                html += """
                    <div class="status success">
                        <p>Authentication successful!</p>
                    </div>
                    <p>You have successfully authenticated with Gmail.</p>
                    <form action="/process" method="get">
                        <button type="submit">Process {} Unread Emails</button>
                    </form>
                """.format(message_count)
                html += html_end
                
            except Exception as e:
                html = html_start
                html += """
                    <div class="status error">
                        <p>Authentication failed: {}</p>
                    </div>
                    <p>Please try again:</p>
                    <form action="/auth" method="get">
                        <button type="submit">Retry Authorization</button>
                    </form>
                """.format(str(e))
                html += html_end
            
            self.wfile.write(html.encode())
            
        elif path == '/process':
            # Process emails
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>BRIX Gmail Auto-Reply</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                    h1 { color: #0066cc; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .info { background-color: #d9edf7; color: #31708f; }
                    pre { background-color: #f5f5f5; padding: 10px; border-radius: 5px; overflow-x: auto; }
                </style>
                <meta http-equiv="refresh" content="2;url=/results">
            </head>
            <body>
                <div class="container">
                    <h1>BRIX Gmail Auto-Reply</h1>
                    <div class="status info">
                        <p>Processing unread emails...</p>
                    </div>
                    <pre>Starting to process up to {} unread emails...</pre>
                </div>
            </body>
            </html>
            """.format(message_count)
            
            self.wfile.write(html.encode())
            
            # Process in background
            self.server.process_thread = True
            
        elif path == '/results':
            # Show results
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            html_start = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>BRIX Gmail Auto-Reply</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 0; padding: 20px; line-height: 1.6; }
                    h1 { color: #0066cc; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
                    .success { background-color: #dff0d8; color: #3c763d; }
                    .info { background-color: #d9edf7; color: #31708f; }
                    button { background-color: #0066cc; color: white; border: none; padding: 10px 15px; cursor: pointer; }
                </style>
            """
            
            html_end = """
                </div>
            </body>
            </html>
            """
            
            if processed_count > 0:
                html = html_start
                html += """
                </head>
                <body>
                    <div class="container">
                        <h1>BRIX Gmail Auto-Reply</h1>
                        <div class="status success">
                            <p>Email processing completed!</p>
                        </div>
                        <p>Processed: <b>{}</b> emails</p>
                        <p>Successful replies: <b>{}</b></p>
                        <p>Errors: <b>{}</b></p>
                        <p>Thank you for using BRIX Gmail Auto-Reply.</p>
                        <form action="/" method="get">
                            <button type="submit">Start Over</button>
                        </form>
                """.format(processed_count, success_count, error_count)
                html += html_end
            else:
                html = html_start
                html += """
                    <meta http-equiv="refresh" content="2;url=/results">
                </head>
                <body>
                    <div class="container">
                        <h1>BRIX Gmail Auto-Reply</h1>
                        <div class="status info">
                            <p>Processing emails...</p>
                        </div>
                        <p>Please wait while we process your emails.</p>
                """
                html += html_end
            
            self.wfile.write(html.encode())
            
        else:
            # Not found
            self.send_response(404)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'404 Not Found')

def process_emails():
    """Process unread emails."""
    global credentials, message_count, processed_count, success_count, error_count
    
    try:
        # Build Gmail API service
        service = build('gmail', 'v1', credentials=credentials)
        
        # Get unread messages
        results = service.users().messages().list(
            userId='me',
            labelIds=['INBOX'],
            q='is:unread',
            maxResults=message_count
        ).execute()
        
        messages = results.get('messages', [])
        
        if not messages:
            processed_count = 0
            return
        
        # Process each message
        for message in messages:
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
                
                # Mark as read
                service.users().messages().modify(
                    userId='me',
                    id=message['id'],
                    body={'removeLabelIds': ['UNREAD']}
                ).execute()
                
                success_count += 1
                
            except Exception as e:
                print(f"Error processing message: {e}")
                error_count += 1
            
            processed_count += 1
            
    except Exception as e:
        print(f"Error: {e}")

def run_server():
    """Run the web server."""
    server = HTTPServer(('localhost', 8080), GmailHandler)
    
    # Add process_thread attribute
    server.process_thread = False
    
    print("\n=== BRIX Gmail Auto-Reply Web Server ===")
    print("Server started at http://localhost:8080")
    print("Opening browser...")
    
    # Open browser
    webbrowser.open('http://localhost:8080')
    
    # Run server
    while True:
        server.handle_request()
        
        # Check if we need to process emails
        if server.process_thread:
            server.process_thread = False
            process_emails()

def main():
    """Main function."""
    global message_count
    
    # Get message count from command line
    if len(sys.argv) > 1:
        try:
            message_count = int(sys.argv[1])
        except:
            pass
    
    # Run server
    run_server()

if __name__ == "__main__":
    main()