import sqlite3
import os
import shutil

DB_FILE = 'data/keywords.db'
BACKUP_FILE = 'data/keywords_backup.db'

def backup_database():
    if os.path.exists(DB_FILE):
        shutil.copy(DB_FILE, BACKUP_FILE)
        print(f"已备份数据库到: {BACKUP_FILE}")

def migrate_tables():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS io_disc_new")
    cursor.execute("""
        CREATE TABLE io_disc_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT,
            comment TEXT,
            access_name TEXT,
            item_name TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO io_disc_new (tag_name, comment, access_name, item_name)
        SELECT 
            COALESCE(tag_name, ''),
            COALESCE(comment, ''),
            COALESCE(access_name, ''),
            COALESCE(item_name, '')
        FROM io_disc
    """)
    cursor.execute("DROP TABLE io_disc")
    cursor.execute("ALTER TABLE io_disc_new RENAME TO io_disc")
    print(f"io_disc 表已精简，保留列: tag_name, comment, access_name, item_name")
    
    cursor.execute("DROP TABLE IF EXISTS io_int_new")
    cursor.execute("""
        CREATE TABLE io_int_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT,
            comment TEXT,
            eng_units TEXT,
            min_value REAL,
            max_value REAL,
            lolo_alarm_state INTEGER,
            lolo_alarm_value REAL,
            lolo_alarm_pri INTEGER,
            lo_alarm_state INTEGER,
            lo_alarm_value REAL,
            lo_alarm_pri INTEGER,
            hi_alarm_state INTEGER,
            hi_alarm_value REAL,
            hi_alarm_pri INTEGER,
            hihi_alarm_state INTEGER,
            hihi_alarm_value REAL,
            hihi_alarm_pri INTEGER,
            access_name TEXT,
            item_name TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO io_int_new (
            tag_name, comment, eng_units, min_value, max_value,
            lolo_alarm_state, lolo_alarm_value, lolo_alarm_pri,
            lo_alarm_state, lo_alarm_value, lo_alarm_pri,
            hi_alarm_state, hi_alarm_value, hi_alarm_pri,
            hihi_alarm_state, hihi_alarm_value, hihi_alarm_pri,
            access_name, item_name
        )
        SELECT 
            COALESCE(tag_name, ''),
            COALESCE(comment, ''),
            COALESCE(eng_units, ''),
            COALESCE(min_value, 0),
            COALESCE(max_value, 0),
            COALESCE(lolo_alarm_state, 0),
            COALESCE(lolo_alarm_value, 0),
            COALESCE(lolo_alarm_pri, 0),
            COALESCE(lo_alarm_state, 0),
            COALESCE(lo_alarm_value, 0),
            COALESCE(lo_alarm_pri, 0),
            COALESCE(hi_alarm_state, 0),
            COALESCE(hi_alarm_value, 0),
            COALESCE(hi_alarm_pri, 0),
            COALESCE(hihi_alarm_state, 0),
            COALESCE(hihi_alarm_value, 0),
            COALESCE(hihi_alarm_pri, 0),
            COALESCE(access_name, ''),
            COALESCE(item_name, '')
        FROM io_int
    """)
    cursor.execute("DROP TABLE io_int")
    cursor.execute("ALTER TABLE io_int_new RENAME TO io_int")
    print(f"io_int 表已精简")
    
    cursor.execute("DROP TABLE IF EXISTS io_real_new")
    cursor.execute("""
        CREATE TABLE io_real_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tag_name TEXT,
            comment TEXT,
            eng_units TEXT,
            min_eu REAL,
            max_eu REAL,
            lolo_alarm_state INTEGER,
            lolo_alarm_value REAL,
            lolo_alarm_pri INTEGER,
            lo_alarm_state INTEGER,
            lo_alarm_value REAL,
            lo_alarm_pri INTEGER,
            hi_alarm_state INTEGER,
            hi_alarm_value REAL,
            hi_alarm_pri INTEGER,
            hihi_alarm_state INTEGER,
            hihi_alarm_value REAL,
            hihi_alarm_pri INTEGER,
            access_name TEXT,
            item_name TEXT
        )
    """)
    cursor.execute("""
        INSERT INTO io_real_new (
            tag_name, comment, eng_units, min_eu, max_eu,
            lolo_alarm_state, lolo_alarm_value, lolo_alarm_pri,
            lo_alarm_state, lo_alarm_value, lo_alarm_pri,
            hi_alarm_state, hi_alarm_value, hi_alarm_pri,
            hihi_alarm_state, hihi_alarm_value, hihi_alarm_pri,
            access_name, item_name
        )
        SELECT 
            COALESCE(tag_name, ''),
            COALESCE(comment, ''),
            COALESCE(eng_units, ''),
            COALESCE(min_eu, 0),
            COALESCE(max_eu, 0),
            COALESCE(lolo_alarm_state, 0),
            COALESCE(lolo_alarm_value, 0),
            COALESCE(lolo_alarm_pri, 0),
            COALESCE(lo_alarm_state, 0),
            COALESCE(lo_alarm_value, 0),
            COALESCE(lo_alarm_pri, 0),
            COALESCE(hi_alarm_state, 0),
            COALESCE(hi_alarm_value, 0),
            COALESCE(hi_alarm_pri, 0),
            COALESCE(hihi_alarm_state, 0),
            COALESCE(hihi_alarm_value, 0),
            COALESCE(hihi_alarm_pri, 0),
            COALESCE(access_name, ''),
            COALESCE(item_name, '')
        FROM io_real
    """)
    cursor.execute("DROP TABLE io_real")
    cursor.execute("ALTER TABLE io_real_new RENAME TO io_real")
    print(f"io_real 表已精简")
    
    conn.commit()
    
    cursor.execute("PRAGMA table_info(io_disc)")
    print(f"\nio_disc 列: {[r[1] for r in cursor.fetchall()]}")
    cursor.execute("PRAGMA table_info(io_int)")
    print(f"io_int 列: {[r[1] for r in cursor.fetchall()]}")
    cursor.execute("PRAGMA table_info(io_real)")
    print(f"io_real 列: {[r[1] for r in cursor.fetchall()]}")
    
    conn.close()
    print("\n数据库迁移完成!")

if __name__ == '__main__':
    backup_database()
    migrate_tables()
