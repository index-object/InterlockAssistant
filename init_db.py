import sqlite3
import os

os.makedirs('data', exist_ok=True)

conn = sqlite3.connect('data/keywords.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()

print("Database initialized successfully!")