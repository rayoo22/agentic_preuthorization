import openai
import os
import json

class OpenAIEmailAgent:
    def __init__(self, model='gpt-4o'):
        openai.api_key = os.getenv('OPENAI_API_KEY')
        self.model = model
    
    def generate_email_response(self, subject, body, sender, attachments=None):
        prompt = f"""You are an AI email assistant. Analyze the following email and generate a professional response.

Email Details:
From: {sender}
Subject: {subject}

Body:
{body}

{f"Attachments: {len(attachments)} file(s)" if attachments else "No attachments"}

Generate a professional, concise email response addressing the key points."""

        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a professional email assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        return response.choices[0].message.content
    
    def extract_claim_data(self, subject, body):
        prompt = f"""Extract claim information from this email. Return ONLY a JSON object with these fields:
- member_id
- diagnosis
- requested_service
- claim_amount (numeric value only)

Email Subject: {subject}
Email Body: {body}

Return JSON only, no explanation."""

        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You extract structured data from emails. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        
        try:
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            return json.loads(content)
        except:
            return None
    
    def clinical_adjudication(self, diagnosis, requested_service, policy_context=None):
        context_section = ""
        if policy_context:
            context_section = f"\n\nPolicy Context:\n{json.dumps(policy_context, indent=2)}\n\nConsider the policy terms, coverage limits, and exclusions when making your decision."
        
        prompt = f"""You are a clinical adjudicator. Evaluate if the requested service is medically necessary for the diagnosis.{context_section}

Diagnosis: {diagnosis}
Requested Service: {requested_service}

Return ONLY a JSON object:
{{
  "decision": "APPROVED" or "DENIED",
  "reasoning": "brief clinical justification considering policy terms"
}}

Return JSON only."""

        response = openai.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a clinical adjudicator with access to policy information. Return only valid JSON."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        
        try:
            content = response.choices[0].message.content.strip()
            if content.startswith('```json'):
                content = content[7:-3].strip()
            elif content.startswith('```'):
                content = content[3:-3].strip()
            return json.loads(content)
        except:
            return {"decision": "PENDING", "reasoning": "Unable to process"}
