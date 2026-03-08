import sqlite3

DB_FILE = 'data/keywords.db'

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

tables_to_drop = ['io_access', 'memory_disc', 'memory_real', 'alarm_group']

for table in tables_to_drop:
    try:
        cursor.execute(f'DROP TABLE {table}')
        print(f'已删除表: {table}')
    except Exception as e:
        print(f'删除表 {table} 失败: {e}')

conn.commit()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
all_tables = [t[0] for t in cursor.fetchall()]
print(f'\n当前数据库表: {all_tables}')

conn.close()
