import psycopg2
from psycopg2.extras import execute_values, Json
import os

class EmailDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        self.create_table()
    
    def create_table(self):
        with self.conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS emails (
                    message_id VARCHAR(255) PRIMARY KEY,
                    sender VARCHAR(255),
                    subject TEXT,
                    date TIMESTAMP,
                    body_snippet TEXT,
                    attachments JSONB,
                    status VARCHAR(20) DEFAULT 'new',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS claims (
                    claim_id SERIAL PRIMARY KEY,
                    member_id VARCHAR(100),
                    diagnosis TEXT,
                    requested_service TEXT,
                    claim_amount DECIMAL(10, 2),
                    adjudication_reasoning TEXT,
                    status VARCHAR(20) DEFAULT 'NEW',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            self.conn.commit()
    
    def email_exists(self, message_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT 1 FROM emails WHERE message_id = %s", (message_id,))
            return cur.fetchone() is not None
    
    def insert_email(self, email_data):
        if self.email_exists(email_data['message_id']):
            return False
        
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO emails (message_id, sender, subject, date, body_snippet, attachments, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                email_data['message_id'],
                email_data['sender'],
                email_data['subject'],
                email_data['date'],
                email_data['body_snippet'],
                Json(email_data.get('attachments', [])),
                email_data.get('status', 'new')
            ))
            self.conn.commit()
            return True
    
    def update_status(self, message_id, status):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE emails SET status = %s WHERE message_id = %s", (status, message_id))
            self.conn.commit()
    
    def insert_claim(self, claim_data):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO claims (claim_id, member_id, diagnosis, requested_service, claim_amount, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING claim_id
            """, (
                claim_data.get('member_id'),
                claim_data.get('diagnosis'),
                claim_data.get('requested_service'),
                claim_data.get('claim_amount'),
                'NEW'
            ))
            self.conn.commit()
            return cur.fetchone()[0]
    
    def update_claim_status(self, claim_id, status):
        with self.conn.cursor() as cur:
            cur.execute("UPDATE claims SET status = %s WHERE claim_id = %s", (status, claim_id))
            self.conn.commit()
    
    def get_claim(self, claim_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT member_id, diagnosis, requested_service, claim_amount, status FROM claims WHERE claim_id = %s", (claim_id,))
            row = cur.fetchone()
            if row:
                return {
                    'member_id': row[0],
                    'diagnosis': row[1],
                    'requested_service': row[2],
                    'claim_amount': row[3],
                    'status': row[4]
                }
            return None
    
    def close(self):
        self.conn.close()
