from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import pickle
from datetime import datetime
from email.utils import parsedate_to_datetime

SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

class GmailReader:
    def __init__(self):
        self.service = self._authenticate()
    
    def _authenticate(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        
        return build('gmail', 'v1', credentials=creds)
    
    def fetch_emails(self, max_results=10, label_name=None, unread_only=False):
        query_parts = []
        if label_name:
            query_parts.append(f'label:{label_name}')
        else:
            query_parts.append('in:inbox')
        
        if unread_only:
            query_parts.append('is:unread')
        
        query = ' '.join(query_parts)
        results = self.service.users().messages().list(userId='me', q=query, maxResults=max_results).execute()
        messages = results.get('messages', [])
        
        emails = []
        for msg in messages:
            email_data = self._get_email_details(msg['id'])
            if email_data:
                emails.append(email_data)
        
        return emails
    
    def _get_email_details(self, msg_id):
        msg = self.service.users().messages().get(userId='me', id=msg_id, format='full').execute()
        
        headers = msg['payload']['headers']
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')
        date_str = next((h['value'] for h in headers if h['name'] == 'Date'), None)
        
        date = parsedate_to_datetime(date_str) if date_str else None
        
        return {
            'message_id': msg['id'],
            'sender': sender,
            'subject': subject,
            'date': date,
            'body_snippet': msg.get('snippet', '')
        }
    
    def mark_as_read(self, msg_id):
        self.service.users().messages().modify(
            userId='me',
            id=msg_id,
            body={'removeLabelIds': ['UNREAD']}
        ).execute()
