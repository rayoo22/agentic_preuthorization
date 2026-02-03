import psycopg2
import os

class MembersDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    
    def get_member(self, member_id):
        with self.conn.cursor() as cur:
            cur.execute("""
                SELECT member_id, full_name, date_of_birth, policy_id, status, policy_balance 
                FROM members 
                WHERE member_id = %s
            """, (member_id,))
            row = cur.fetchone()
            if row:
                return {
                    'member_id': row[0],
                    'full_name': row[1],
                    'date_of_birth': row[2],
                    'policy_id': row[3],
                    'status': row[4],
                    'policy_balance': float(row[5])
                }
            return None
    
    def deduct_from_balance(self, member_id, amount):
        with self.conn.cursor() as cur:
            cur.execute("""
                UPDATE members 
                SET policy_balance = policy_balance - %s 
                WHERE member_id = %s
            """, (amount, member_id))
            self.conn.commit()
    
    def close(self):
        self.conn.close()
