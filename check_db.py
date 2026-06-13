import sqlite3
import os

db_path = "backend/malnutrition.db"
if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("--- USERS ---")
cursor.execute("SELECT id, full_name, email FROM users")
for row in cursor.fetchall():
    print(row)

print("\n--- CHILDREN ---")
cursor.execute("SELECT id, name, worker_id FROM children")
for row in cursor.fetchall():
    print(row)

conn.close()
