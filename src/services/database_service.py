import sqlite3
import os
from typing import List, Dict, Optional

class DatabaseService:
    def __init__(self, db_path: str = "data/keywords.db"):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS io_access (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                access_name TEXT NOT NULL,
                application TEXT,
                topic TEXT,
                advise_active TEXT,
                dde_protocol TEXT,
                sec_application TEXT,
                sec_topic TEXT,
                sec_advise_active TEXT,
                sec_dde_protocol TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS io_disc (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL,
                group_name TEXT,
                comment TEXT,
                logged TEXT,
                event_logged TEXT,
                event_logging_priority INTEGER,
                retentive_value TEXT,
                initial_disc TEXT,
                off_msg TEXT,
                on_msg TEXT,
                alarm_state TEXT,
                alarm_pri INTEGER,
                d_conversion TEXT,
                access_name TEXT,
                item_use_tagname TEXT,
                item_name TEXT,
                read_only TEXT,
                alarm_comment TEXT,
                alarm_ack_model INTEGER,
                dsc_alarm_disable INTEGER,
                dsc_alarm_inhibitor INTEGER,
                symbolic_name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.execute('''
            CREATE TABLE IF NOT EXISTS io_real (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tag_name TEXT NOT NULL,
                group_name TEXT,
                comment TEXT,
                logged TEXT,
                event_logged TEXT,
                event_logging_priority INTEGER,
                retentive_value TEXT,
                retentive_alarm_parameters TEXT,
                alarm_value_deadband REAL,
                alarm_dev_deadband REAL,
                eng_units TEXT,
                initial_value REAL,
                min_eu REAL,
                max_eu REAL,
                deadband REAL,
                log_deadband REAL,
                lolo_alarm_state TEXT,
                lolo_alarm_value REAL,
                lolo_alarm_pri INTEGER,
                lo_alarm_state TEXT,
                lo_alarm_value REAL,
                lo_alarm_pri INTEGER,
                hi_alarm_state TEXT,
                hi_alarm_value REAL,
                hi_alarm_pri INTEGER,
                hihi_alarm_state TEXT,
                hihi_alarm_value REAL,
                hihi_alarm_pri INTEGER,
                minor_dev_alarm_state TEXT,
                minor_dev_alarm_value REAL,
                minor_dev_alarm_pri INTEGER,
                major_dev_alarm_state TEXT,
                major_dev_alarm_value REAL,
                major_dev_alarm_pri INTEGER,
                dev_target TEXT,
                roc_alarm_state TEXT,
                roc_alarm_value REAL,
                roc_alarm_pri INTEGER,
                roc_time_base TEXT,
                min_raw INTEGER,
                max_raw INTEGER,
                conversion TEXT,
                access_name TEXT,
                item_use_tagname TEXT,
                item_name TEXT,
                read_only TEXT,
                alarm_comment TEXT,
                alarm_ack_model INTEGER,
                lolo_alarm_disable INTEGER,
                lo_alarm_disable INTEGER,
                hi_alarm_disable INTEGER,
                hihi_alarm_disable INTEGER,
                min_dev_alarm_disable INTEGER,
                maj_dev_alarm_disable INTEGER,
                roc_alarm_disable INTEGER,
                lolo_alarm_inhibitor TEXT,
                lo_alarm_inhibitor TEXT,
                hi_alarm_inhibitor TEXT,
                hihi_alarm_inhibitor TEXT,
                min_dev_alarm_inhibitor TEXT,
                maj_dev_alarm_inhibitor TEXT,
                roc_alarm_inhibitor TEXT,
                symbolic_name TEXT,
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

    def search_io_disc(self, text: str) -> List[Dict]:
        if not text:
            return []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM io_disc WHERE tag_name LIKE ? OR comment LIKE ? OR item_name LIKE ?", 
                       (f'%{text}%', f'%{text}%', f'%{text}%'))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def search_io_real(self, text: str) -> List[Dict]:
        if not text:
            return []
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM io_real WHERE tag_name LIKE ? OR comment LIKE ? OR item_name LIKE ?", 
                       (f'%{text}%', f'%{text}%', f'%{text}%'))
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_all_io_disc(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM io_disc ORDER BY tag_name")
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_all_io_real(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM io_real ORDER BY tag_name")
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def get_io_disc_by_tagname(self, tag_name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM io_disc WHERE tag_name = ?", (tag_name,))
        row = cursor.fetchone()
        result = dict(row) if row else None
        conn.close()
        return result
    
    def get_io_real_by_tagname(self, tag_name: str) -> Optional[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM io_real WHERE tag_name = ?", (tag_name,))
        row = cursor.fetchone()
        result = dict(row) if row else None
        conn.close()
        return result
    
    def search_all_io_tags(self, text: str) -> List[Dict]:
        if not text:
            return []
        
        disc_results = self.search_io_disc(text)
        real_results = self.search_io_real(text)
        
        for r in disc_results:
            r['tag_type'] = 'IODisc'
        for r in real_results:
            r['tag_type'] = 'IOReal'
        
        return disc_results + real_results