import psycopg2
import os
from decimal import Decimal

class PoliciesDB:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=os.getenv('DB_PORT'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
    
    def get_policy(self, policy_id):
        with self.conn.cursor() as cur:
            cur.execute("SELECT * FROM policies WHERE policy_id = %s", (policy_id,))
            columns = [desc[0] for desc in cur.description]
            row = cur.fetchone()
            if row:
                policy_dict = dict(zip(columns, row))
                # Convert Decimal to float for JSON serialization
                for key, value in policy_dict.items():
                    if isinstance(value, Decimal):
                        policy_dict[key] = float(value)
                return policy_dict
            return None
    
    def close(self):
        self.conn.close()
