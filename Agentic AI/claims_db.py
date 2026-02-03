import psycopg2
import os

class ClaimsDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    
    def insert_claim(self, member_id, diagnosis, requested_service, claim_amount):
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO claims (member_id, diagnosis, requested_service, claim_amount, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING claim_id
            """, (member_id, diagnosis, requested_service, claim_amount, 'PENDING'))
            self.conn.commit()
            return cur.fetchone()[0]
    
    def update_claim_status(self, claim_id, status, reasoning=None):
        with self.conn.cursor() as cur:
            if reasoning:
                cur.execute("""
                    UPDATE claims 
                    SET status = %s, adjudication_reasoning = %s
                    WHERE claim_id = %s
                """, (status, reasoning, claim_id))
            else:
                cur.execute("""
                    UPDATE claims 
                    SET status = %s
                    WHERE claim_id = %s
                """, (status, claim_id))
            self.conn.commit()
    
    def close(self):
        self.conn.close()
