import sqlite3
import csv
import os
import sys
import logging

logging.basicConfig(filename='import_debug.log', level=logging.DEBUG, encoding='utf-8')
logger = logging.getLogger()

CSV_FILE = '导入数据/合成.CSV'
DB_FILE = 'data/keywords.db'

def clean_value(val):
    if val is None or val == '':
        return None
    val = val.strip()
    if val.upper() == 'YES':
        return 'Yes'
    if val.upper() == 'NO':
        return 'No'
    return val if val else None

def parse_csv_sections():
    sections = {}
    current_section = None
    current_headers = []
    current_data = []
    
    with open(CSV_FILE, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0]:
                continue
            
            first_cell = row[0].strip()
            
            if first_cell.startswith(':') and not first_cell.startswith(':"'):
                if current_section and current_data:
                    sections[current_section] = {
                        'headers': current_headers,
                        'data': current_data
                    }
                
                current_section = first_cell[1:]
                current_headers = [h.strip() for h in row[1:] if h.strip() and h.strip() != '']
                current_data = []
            elif current_section and first_cell and not first_cell.startswith(':'):
                values = []
                for v in row:
                    v = v.strip().strip('"')
                    values.append(clean_value(v))
                while len(values) < len(current_headers):
                    values.append(None)
                current_data.append(values)
    
    if current_section and current_data:
        sections[current_section] = {
            'headers': current_headers,
            'data': current_data
        }
        logger.info(f"Parsed section: {current_section} with {len(current_data)} rows")
    
    return sections

def import_io_access(conn, data):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM io_access")
    
    headers = ['access_name', 'application', 'topic', 'advise_active', 'dde_protocol',
               'sec_application', 'sec_topic', 'sec_advise_active', 'sec_dde_protocol']
    
    for row in data:
        values = []
        for i, h in enumerate(headers):
            if i < len(row):
                values.append(row[i])
            else:
                values.append(None)
        
        cursor.execute('''
            INSERT INTO io_access (access_name, application, topic, advise_active, dde_protocol,
                sec_application, sec_topic, sec_advise_active, sec_dde_protocol)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)
    
    conn.commit()
    print(f"导入 {cursor.rowcount} 条 IOAccess 记录")

def import_io_disc(conn, data):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM io_disc")
    
    headers = ['tag_name', 'group_name', 'comment', 'logged', 'event_logged',
              'event_logging_priority', 'retentive_value', 'initial_disc', 'off_msg', 'on_msg',
              'alarm_state', 'alarm_pri', 'd_conversion', 'access_name', 'item_use_tagname',
              'item_name', 'read_only', 'alarm_comment', 'alarm_ack_model', 'dsc_alarm_disable',
              'dsc_alarm_inhibitor', 'symbolic_name']
    
    for row in data:
        values = []
        for i, h in enumerate(headers):
            if i < len(row):
                val = row[i]
                if h in ['event_logging_priority', 'alarm_pri', 'alarm_ack_model', 'dsc_alarm_disable', 'dsc_alarm_inhibitor']:
                    try:
                        val = int(val) if val else 0
                    except:
                        val = 0
                values.append(val)
            else:
                values.append(None)
        
        cursor.execute('''
            INSERT INTO io_disc (tag_name, group_name, comment, logged, event_logged,
                event_logging_priority, retentive_value, initial_disc, off_msg, on_msg,
                alarm_state, alarm_pri, d_conversion, access_name, item_use_tagname,
                item_name, read_only, alarm_comment, alarm_ack_model, dsc_alarm_disable,
                dsc_alarm_inhibitor, symbolic_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', values)
    
    conn.commit()
    print(f"导入 {cursor.rowcount} 条 IODisc 记录")

def import_io_int(conn, data):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM io_int")
    
    headers = ['tag_name', 'group_name', 'comment', 'logged', 'event_logged',
              'event_logging_priority', 'retentive_value', 'retentive_alarm_parameters',
              'alarm_value_deadband', 'alarm_dev_deadband', 'eng_units', 'initial_value',
              'min_value', 'max_value', 'deadband', 'log_deadband', 'lolo_alarm_state',
              'lolo_alarm_value', 'lolo_alarm_pri', 'lo_alarm_state', 'lo_alarm_value',
              'lo_alarm_pri', 'hi_alarm_state', 'hi_alarm_value', 'hi_alarm_pri',
              'hihi_alarm_state', 'hihi_alarm_value', 'hihi_alarm_pri', 'minor_dev_alarm_state',
              'minor_dev_alarm_value', 'minor_dev_alarm_pri', 'major_dev_alarm_state',
              'major_dev_alarm_value', 'major_dev_alarm_pri', 'dev_target', 'roc_alarm_state',
              'roc_alarm_value', 'roc_alarm_pri', 'roc_time_base', 'min_raw', 'max_raw',
              'conversion', 'access_name', 'item_use_tagname', 'item_name', 'read_only',
              'alarm_comment', 'alarm_ack_model', 'lolo_alarm_disable', 'lo_alarm_disable',
              'hi_alarm_disable', 'hihi_alarm_disable', 'min_dev_alarm_disable',
              'maj_dev_alarm_disable', 'roc_alarm_disable', 'lolo_alarm_inhibitor',
              'lo_alarm_inhibitor', 'hi_alarm_inhibitor', 'hihi_alarm_inhibitor',
              'min_dev_alarm_inhibitor', 'maj_dev_alarm_inhibitor', 'roc_alarm_inhibitor',
              'symbolic_name']
    
    for row in data:
        values = []
        for i, h in enumerate(headers):
            if i < len(row):
                val = row[i]
                if h in ['event_logging_priority', 'lolo_alarm_pri', 'lo_alarm_pri', 'hi_alarm_pri',
                        'hihi_alarm_pri', 'minor_dev_alarm_pri', 'major_dev_alarm_pri',
                        'roc_alarm_pri', 'min_raw', 'max_raw', 'alarm_ack_model',
                        'lolo_alarm_disable', 'lo_alarm_disable', 'hi_alarm_disable',
                        'hihi_alarm_disable', 'min_dev_alarm_disable', 'maj_dev_alarm_disable',
                        'roc_alarm_disable']:
                    try:
                        val = int(val) if val else 0
                    except:
                        val = 0
                elif h in ['alarm_value_deadband', 'alarm_dev_deadband', 'initial_value',
                          'min_value', 'max_value', 'deadband', 'log_deadband',
                          'lolo_alarm_value', 'lo_alarm_value', 'hi_alarm_value',
                          'hihi_alarm_value', 'minor_dev_alarm_value', 'major_dev_alarm_value',
                          'roc_alarm_value']:
                    try:
                        val = float(val) if val else 0.0
                    except:
                        val = 0.0
                values.append(val)
            else:
                values.append(None)
        
        cursor.execute(f'''
            INSERT INTO io_int ({', '.join(headers)})
            VALUES ({', '.join(['?'] * len(headers))})
        ''', values)
    
    conn.commit()
    print(f"导入 {cursor.rowcount} 条 IOInt 记录")

def import_io_real(conn, data):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM io_real")
    
    headers = ['tag_name', 'group_name', 'comment', 'logged', 'event_logged',
              'event_logging_priority', 'retentive_value', 'retentive_alarm_parameters',
              'alarm_value_deadband', 'alarm_dev_deadband', 'eng_units', 'initial_value',
              'min_eu', 'max_eu', 'deadband', 'log_deadband', 'lolo_alarm_state',
              'lolo_alarm_value', 'lolo_alarm_pri', 'lo_alarm_state', 'lo_alarm_value',
              'lo_alarm_pri', 'hi_alarm_state', 'hi_alarm_value', 'hi_alarm_pri',
              'hihi_alarm_state', 'hihi_alarm_value', 'hihi_alarm_pri', 'minor_dev_alarm_state',
              'minor_dev_alarm_value', 'minor_dev_alarm_pri', 'major_dev_alarm_state',
              'major_dev_alarm_value', 'major_dev_alarm_pri', 'dev_target', 'roc_alarm_state',
              'roc_alarm_value', 'roc_alarm_pri', 'roc_time_base', 'min_raw', 'max_raw',
              'conversion', 'access_name', 'item_use_tagname', 'item_name', 'read_only',
              'alarm_comment', 'alarm_ack_model', 'lolo_alarm_disable', 'lo_alarm_disable',
              'hi_alarm_disable', 'hihi_alarm_disable', 'min_dev_alarm_disable',
              'maj_dev_alarm_disable', 'roc_alarm_disable', 'lolo_alarm_inhibitor',
              'lo_alarm_inhibitor', 'hi_alarm_inhibitor', 'hihi_alarm_inhibitor',
              'min_dev_alarm_inhibitor', 'maj_dev_alarm_inhibitor', 'roc_alarm_inhibitor',
              'symbolic_name']
    
    for row in data:
        values = []
        for i, h in enumerate(headers):
            if i < len(row):
                val = row[i]
                if h in ['event_logging_priority', 'lolo_alarm_pri', 'lo_alarm_pri', 'hi_alarm_pri',
                        'hihi_alarm_pri', 'minor_dev_alarm_pri', 'major_dev_alarm_pri',
                        'roc_alarm_pri', 'min_raw', 'max_raw', 'alarm_ack_model',
                        'lolo_alarm_disable', 'lo_alarm_disable', 'hi_alarm_disable',
                        'hihi_alarm_disable', 'min_dev_alarm_disable', 'maj_dev_alarm_disable',
                        'roc_alarm_disable']:
                    try:
                        val = int(val) if val else 0
                    except:
                        val = 0
                elif h in ['alarm_value_deadband', 'alarm_dev_deadband', 'initial_value',
                          'min_eu', 'max_eu', 'deadband', 'log_deadband',
                          'lolo_alarm_value', 'lo_alarm_value', 'hi_alarm_value',
                          'hihi_alarm_value', 'minor_dev_alarm_value', 'major_dev_alarm_value',
                          'roc_alarm_value']:
                    try:
                        val = float(val) if val else 0.0
                    except:
                        val = 0.0
                values.append(val)
            else:
                values.append(None)
        
        cursor.execute(f'''
            INSERT INTO io_real ({', '.join(headers)})
            VALUES ({', '.join(['?'] * len(headers))})
        ''', values)
    
    conn.commit()
    print(f"导入 {cursor.rowcount} 条 IOReal 记录")

def import_memory_disc(conn, data):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memory_disc")
    
    headers = ['tag_name', 'group_name', 'comment', 'logged', 'event_logged',
              'event_logging_priority', 'retentive_value', 'initial_disc', 'off_msg', 'on_msg',
              'alarm_state', 'alarm_pri', 'alarm_comment', 'alarm_ack_model',
              'dsc_alarm_disable', 'dsc_alarm_inhibitor', 'symbolic_name']
    
    for row in data:
        values = []
        for i, h in enumerate(headers):
            if i < len(row):
                val = row[i]
                if h in ['event_logging_priority', 'alarm_pri', 'alarm_ack_model',
                        'dsc_alarm_disable', 'dsc_alarm_inhibitor']:
                    try:
                        val = int(val) if val else 0
                    except:
                        val = 0
                values.append(val)
            else:
                values.append(None)
        
        cursor.execute(f'''
            INSERT INTO memory_disc ({', '.join(headers)})
            VALUES ({', '.join(['?'] * len(headers))})
        ''', values)
    
    conn.commit()
    print(f"导入 {cursor.rowcount} 条 MemoryDisc 记录")

def import_memory_real(conn, data):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM memory_real")
    
    headers = ['tag_name', 'group_name', 'comment', 'logged', 'event_logged',
              'event_logging_priority', 'retentive_value', 'retentive_alarm_parameters',
              'alarm_value_deadband', 'alarm_dev_deadband', 'eng_units', 'initial_value',
              'min_value', 'max_value', 'deadband', 'log_deadband', 'lolo_alarm_state',
              'lolo_alarm_value', 'lolo_alarm_pri', 'lo_alarm_state', 'lo_alarm_value',
              'lo_alarm_pri', 'hi_alarm_state', 'hi_alarm_value', 'hi_alarm_pri',
              'hihi_alarm_state', 'hihi_alarm_value', 'hihi_alarm_pri', 'minor_dev_alarm_state',
              'minor_dev_alarm_value', 'minor_dev_alarm_pri', 'major_dev_alarm_state',
              'major_dev_alarm_value', 'major_dev_alarm_pri', 'dev_target', 'roc_alarm_state',
              'roc_alarm_value', 'roc_alarm_pri', 'roc_time_base', 'alarm_comment',
              'alarm_ack_model', 'lolo_alarm_disable', 'lo_alarm_disable', 'hi_alarm_disable',
              'hihi_alarm_disable', 'min_dev_alarm_disable', 'maj_dev_alarm_disable',
              'roc_alarm_disable', 'lolo_alarm_inhibitor', 'lo_alarm_inhibitor',
              'hi_alarm_inhibitor', 'hihi_alarm_inhibitor', 'min_dev_alarm_inhibitor',
              'maj_dev_alarm_inhibitor', 'roc_alarm_inhibitor', 'symbolic_name']
    
    for row in data:
        values = []
        for i, h in enumerate(headers):
            if i < len(row):
                val = row[i]
                if h in ['event_logging_priority', 'lolo_alarm_pri', 'lo_alarm_pri', 'hi_alarm_pri',
                        'hihi_alarm_pri', 'minor_dev_alarm_pri', 'major_dev_alarm_pri',
                        'roc_alarm_pri', 'alarm_ack_model', 'lolo_alarm_disable',
                        'lo_alarm_disable', 'hi_alarm_disable', 'hihi_alarm_disable',
                        'min_dev_alarm_disable', 'maj_dev_alarm_disable', 'roc_alarm_disable']:
                    try:
                        val = int(val) if val else 0
                    except:
                        val = 0
                elif h in ['alarm_value_deadband', 'alarm_dev_deadband', 'initial_value',
                          'min_value', 'max_value', 'deadband', 'log_deadband',
                          'lolo_alarm_value', 'lo_alarm_value', 'hi_alarm_value',
                          'hihi_alarm_value', 'minor_dev_alarm_value', 'major_dev_alarm_value',
                          'roc_alarm_value']:
                    try:
                        val = float(val) if val else 0.0
                    except:
                        val = 0.0
                values.append(val)
            else:
                values.append(None)
        
        cursor.execute(f'''
            INSERT INTO memory_real ({', '.join(headers)})
            VALUES ({', '.join(['?'] * len(headers))})
        ''', values)
    
    conn.commit()
    print(f"导入 {cursor.rowcount} 条 MemoryReal 记录")

def import_alarm_group(conn, data):
    cursor = conn.cursor()
    cursor.execute("DELETE FROM alarm_group")
    
    headers = ['alarm_group', 'group_name', 'comment', 'event_logged',
              'event_logging_priority', 'lolo_alarm_disable', 'lo_alarm_disable',
              'hi_alarm_disable', 'hihi_alarm_disable', 'min_dev_alarm_disable',
              'maj_dev_alarm_disable', 'roc_alarm_disable', 'dsc_alarm_disable',
              'lolo_alarm_inhibitor', 'lo_alarm_inhibitor', 'hi_alarm_inhibitor',
              'hihi_alarm_inhibitor', 'min_dev_alarm_inhibitor', 'maj_dev_alarm_inhibitor',
              'roc_alarm_inhibitor', 'dsc_alarm_inhibitor']
    
    for row in data:
        values = []
        for i, h in enumerate(headers):
            if i < len(row):
                val = row[i]
                if h in ['event_logging_priority', 'lolo_alarm_disable', 'lo_alarm_disable',
                        'hi_alarm_disable', 'hihi_alarm_disable', 'min_dev_alarm_disable',
                        'maj_dev_alarm_disable', 'roc_alarm_disable', 'dsc_alarm_disable']:
                    try:
                        val = int(val) if val else 0
                    except:
                        val = 0
                values.append(val)
            else:
                values.append(None)
        
        cursor.execute(f'''
            INSERT INTO alarm_group ({', '.join(headers)})
            VALUES ({', '.join(['?'] * len(headers))})
        ''', values)
    
    conn.commit()
    print(f"导入 {cursor.rowcount} 条 AlarmGroup 记录")

def main():
    if not os.path.exists(CSV_FILE):
        print(f"错误: 找不到CSV文件: {CSV_FILE}")
        sys.exit(1)
    
    print(f"正在解析 CSV 文件: {CSV_FILE}")
    sys.stdout.flush()
    sections = parse_csv_sections()
    print(f"解析完成, 共 {len(sections)} 个区块")
    print(f"区块列表: {list(sections.keys())}")
    sys.stdout.flush()
    
    conn = sqlite3.connect(DB_FILE)
    
    try:
        if 'IOAccess' in sections:
            import_io_access(conn, sections['IOAccess']['data'])
        
        if 'IODisc' in sections:
            import_io_disc(conn, sections['IODisc']['data'])
        
        if 'IOInt' in sections:
            import_io_int(conn, sections['IOInt']['data'])
        
        if 'IOReal' in sections:
            import_io_real(conn, sections['IOReal']['data'])
        
        if 'MemoryDisc' in sections:
            import_memory_disc(conn, sections['MemoryDisc']['data'])
        
        if 'MemoryReal' in sections:
            import_memory_real(conn, sections['MemoryReal']['data'])
        
        if 'AlarmGroup' in sections:
            import_alarm_group(conn, sections['AlarmGroup']['data'])
        
        print("\n数据导入完成!")
        
    except Exception as e:
        print(f"导入错误: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    main()