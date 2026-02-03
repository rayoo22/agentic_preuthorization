from dotenv import load_dotenv
from gmail_reader import GmailReader
from db_manager import EmailDB
from openai_agent import OpenAIEmailAgent
from claims_db import ClaimsDB
from members_db import MembersDB
from policies_db import PoliciesDB
import base64
import os

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

def main():
    load_dotenv()
    
    print("Fetching unread emails from Gmail (Agentic_AI label)...")
    gmail = GmailReader()
    emails = gmail.fetch_emails(max_results=50, label_name='Agentic_AI', unread_only=True)
    print(f"Found {len(emails)} unread emails\n")
    
    email_db = EmailDB()
    claims_db = ClaimsDB()
    members_db = MembersDB()
    policies_db = PoliciesDB()
    agent = OpenAIEmailAgent()
    
    new_count = 0
    duplicate_count = 0
    
    for email in emails:
        if email_db.insert_email(email):
            new_count += 1
            print(f"Added email: {email['subject'][:50]}")
            
            # Extract full body
            full_body = extract_email_body(gmail.service, email['message_id'])
            print(full_body)
            input("Press Enter to continue...")
        

            # Extract claim data using LLM
            claim_data = agent.extract_claim_data(email['subject'], full_body)
            print(claim_data)
            input("Press Enter to continue...")

            if not claim_data:
                print("  Could not extract claim data\n")
                continue
            
            print(f"  Extracted: Member {claim_data.get('member_id')}, ${claim_data.get('claim_amount')}")
            
            # Check member existence and policy balance
            member = members_db.get_member(claim_data['member_id'])
            
            if not member:
                print(f"   Member {claim_data['member_id']} not found")
                claims_db.insert_claim(
                    claim_data['member_id'],
                    claim_data['diagnosis'],
                    claim_data['requested_service'],
                    claim_data['claim_amount']
                )
                claims_db.update_claim_status(
                    claims_db.conn.cursor().lastrowid,
                    'DENIED',
                    'Member not found in system'
                )
                continue
            
            print(f"   Member found: {member['full_name']} (Balance: ${member['policy_balance']})")
            
            # Check policy balance
            if member['policy_balance'] < claim_data['claim_amount']:
                print(f"  Insufficient balance: ${member['policy_balance']} < ${claim_data['claim_amount']}")
                claim_id = claims_db.insert_claim(
                    claim_data['member_id'],
                    claim_data['diagnosis'],
                    claim_data['requested_service'],
                    claim_data['claim_amount']
                )
                claims_db.update_claim_status(
                    claim_id,
                    'DENIED',
                    f'Insufficient policy balance: ${member["policy_balance"]} available, ${claim_data["claim_amount"]} required'
                )
                print(f"    Claim ID {claim_id}: DENIED - Insufficient balance\n")
                gmail.mark_as_read(email['message_id'])
                continue
            
            # Store in claims table
            claim_id = claims_db.insert_claim(
                claim_data['member_id'],
                claim_data['diagnosis'],
                claim_data['requested_service'],
                claim_data['claim_amount']
            )
            print(f"    Stored as Claim ID: {claim_id}")
            
            # Retrieve policy context for RAG
            policy_context = policies_db.get_policy(member['policy_id'])
            if policy_context:
                print(f"    Retrieved policy context: {member['policy_id']}")
            
            # Clinical adjudication using LLM with RAG (only if balance is sufficient)
            adjudication = agent.clinical_adjudication(
                claim_data['diagnosis'],
                claim_data['requested_service'],
                policy_context
            )
            
            # Final decision combines clinical and financial checks
            final_decision = adjudication['decision']
            final_reasoning = f"Policy balance: ${member['policy_balance']}. Clinical: {adjudication['reasoning']}"
            
            # Update claim status
            claims_db.update_claim_status(
                claim_id,
                final_decision,
                final_reasoning
            )
            
            # Deduct from policy balance if approved
            if final_decision == 'APPROVED':
                members_db.deduct_from_balance(claim_data['member_id'], claim_data['claim_amount'])
                new_balance = member['policy_balance'] - claim_data['claim_amount']
                print(f"    Adjudication: {final_decision}")
                print(f"    Reasoning: {final_reasoning}")
                print(f"    Deducted ${claim_data['claim_amount']} from policy balance")
                print(f"    New balance: ${new_balance}\n")
            else:
                print(f"    Adjudication: {final_decision}")
                print(f"    Reasoning: {final_reasoning}\n")
            
            # Mark email as read in Gmail
            gmail.mark_as_read(email['message_id'])
            print(f"    Marked as read in Gmail")
        else:
            duplicate_count += 1
            print(f"Skipped (duplicate): {email['subject'][:50]}")
    
    email_db.close()
    claims_db.close()
    members_db.close()
    policies_db.close()
    
    print(f"\nSummary: {new_count} new emails processed, {duplicate_count} duplicates skipped")

if __name__ == "__main__":
    main()
