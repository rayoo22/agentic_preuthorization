from dotenv import load_dotenv
from gmail_reader import GmailReader
from openai_agent import OpenAIEmailAgent
from claims_db import ClaimsDB
import base64

def extract_email_body(gmail_service, msg_id):
    msg = gmail_service.users().messages().get(userId='me', id=msg_id, format='full').execute()
    payload = msg['payload']
    
    if 'body' in payload and payload['body'].get('data'):
        return base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and part['body'].get('data'):
                return base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
    
    return msg.get('snippet', '')

def process_claims():
    load_dotenv()
    
    print("Fetching emails from Gmail...")
    gmail = GmailReader()
    emails = gmail.fetch_emails(max_results=10)
    print(f"Found {len(emails)} emails\n")
    
    agent = OpenAIEmailAgent()
    claims_db = ClaimsDB()
    
    for email in emails:
        print(f"Processing: {email['subject']}")
        
        # Extract full body
        full_body = extract_email_body(gmail.service, email['message_id'])
        
        # Extract claim data using LLM
        claim_data = agent.extract_claim_data(email['subject'], full_body)
        
        if not claim_data:
            print("  ✗ Could not extract claim data\n")
            continue
        
        print(f"  Extracted: Member {claim_data.get('member_id')}, ${claim_data.get('claim_amount')}")
        
        # Store in claims table
        claim_id = claims_db.insert_claim(
            claim_data['member_id'],
            claim_data['diagnosis'],
            claim_data['requested_service'],
            claim_data['claim_amount']
        )
        print(f"  ✓ Stored as Claim ID: {claim_id}")
        
        # Clinical adjudication using LLM
        adjudication = agent.clinical_adjudication(
            claim_data['diagnosis'],
            claim_data['requested_service']
        )
        
        # Update claim status
        claims_db.update_claim_status(
            claim_id,
            adjudication['decision'],
            adjudication['reasoning']
        )
        
        print(f"  ✓ Adjudication: {adjudication['decision']}")
        print(f"    Reasoning: {adjudication['reasoning']}\n")
    
    claims_db.close()
    print("Claims processing complete!")

if __name__ == "__main__":
    process_claims()
