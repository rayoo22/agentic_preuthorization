from dotenv import load_dotenv
from gmail_reader import GmailReader
from email_extractor import EmailExtractor
from openai_agent import OpenAIEmailAgent
from db_manager import EmailDB

def process_claims_workflow():
    load_dotenv()
    
    gmail = GmailReader()
    extractor = EmailExtractor(gmail.service)
    agent = OpenAIEmailAgent()
    db = EmailDB()
    
    print("Fetching emails...")
    results = gmail.service.users().messages().list(userId='me', maxResults=10).execute()
    messages = results.get('messages', [])
    
    print(f"Processing {len(messages)} emails...\n")
    
    for msg in messages:
        email_content = extractor.extract_full_content(msg['id'])
        print(f"📧 {email_content['subject'][:60]}")
        
        # Step 1: Extract claim data
        claim_data = agent.extract_claim_data(email_content['subject'], email_content['body'])
        
        if not claim_data:
            print("   ⊘ No claim data found\n")
            continue
        
        print(f"   Member: {claim_data.get('member_id')}")
        print(f"   Diagnosis: {claim_data.get('diagnosis')}")
        print(f"   Service: {claim_data.get('requested_service')}")
        print(f"   Amount: ${claim_data.get('claim_amount')}")
        
        # Step 2: Store in claims table with status NEW
        try:
            claim_id = db.insert_claim(claim_data)
            print(f"   ✓ Stored as Claim ID: {claim_id} [Status: NEW]")
            
            # Step 3: Update status to IN_PROGRESS
            db.update_claim_status(claim_id, 'IN_PROGRESS')
            
            # Step 4: Perform clinical adjudication
            adjudication = agent.clinical_adjudication(
                claim_data['diagnosis'],
                claim_data['requested_service']
            )
            
            print(f"   Decision: {adjudication['decision']}")
            print(f"   Reasoning: {adjudication['reasoning']}")
            
            # Step 5: Update status to PROCESSED
            db.update_claim_status(claim_id, 'PROCESSED')
            print(f"   ✓ Updated to [Status: PROCESSED]\n")
            
        except Exception as e:
            print(f"   ✗ Error: {e}")
            if 'claim_id' in locals():
                db.update_claim_status(claim_id, 'FAILED')
            print()
    
    db.close()
    print("Claims processing complete!")

if __name__ == "__main__":
    process_claims_workflow()
