import sqlite3
import os
from typing import List, Dict

class DatabaseService:
    def __init__(self, db_path: str = "data/keywords.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_keyword(self, keyword: str, description: str = "") -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO keywords (keyword, description) VALUES (?, ?)",
            (keyword, description)
        )
        conn.commit()
        result = cursor.lastrowid
        conn.close()
        return result
    
    def search(self, text: str) -> List[Dict]:
        if not text:
            return []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keywords")
        all_keywords = cursor.fetchall()
        
        results = []
        for row in all_keywords:
            keyword = row['keyword']
            if keyword and keyword in text:
                results.append(dict(row))
        
        conn.close()
        return results
    
    def delete_keyword(self, keyword_id: int):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))
        conn.commit()
        conn.close()
    
    def get_all_keywords(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keywords ORDER BY created_at DESC")
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def update_keyword(self, keyword_id: int, keyword: str, description: str):
        conn = sqlite3.connect(self.db_path)
        conn.execute(
            "UPDATE keywords SET keyword = ?, description = ? WHERE id = ?",
            (keyword, description, keyword_id)
        )
        conn.commit()
        conn.close()