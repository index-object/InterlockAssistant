import sys
sys.path.insert(0, '.')
from src.services.database_service import DatabaseService

db = DatabaseService('data/keywords.db')
all_real = db.get_all_io_real()

print(f"Total records: {len(all_real) if all_real else 0}")

if all_real:
    # 打印前20条记录看看格式
    print("Sample tag_names:")
    for r in all_real[:20]:
        print(f"  - {r.get('tag_name')}")
    
    # 查找包含 LZT 的记录
    lzt_records = [r for r in all_real if 'LZT' in r.get('tag_name', '').upper()]
    print(f"\nLZT records: {len(lzt_records)}")
    for r in lzt_records[:10]:
        print(f"  - {r.get('tag_name')}")
    
    # 测试模糊搜索
    result = db.fuzzy_search_tag_name('wLTZ_16103')
    print(f"\nFuzzy search 'wLTZ_16103': {result.get('tag_name') if result else 'None'}")