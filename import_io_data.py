import os
import sys
from src.services.database_service import DatabaseService
from src.services.csv_importer import ImportResult


CSV_FILE = '导入数据/合成.CSV'
DB_FILE = 'data/keywords.db'


def main():
    if not os.path.exists(CSV_FILE):
        print(f"错误: 找不到CSV文件: {CSV_FILE}")
        sys.exit(1)
    
    print(f"正在解析 CSV 文件: {CSV_FILE}")
    sys.stdout.flush()
    
    db_service = DatabaseService(DB_FILE)
    result: ImportResult = db_service.import_from_csv(CSV_FILE, mode='replace')
    
    if result.errors:
        print(f"导入错误: {', '.join(result.errors)}")
        sys.exit(1)
    
    print(f"\n导入完成!")
    print(f"  IODisc: {result.iodisc_count} 条")
    print(f"  IOReal: {result.ioreal_count} 条")
    print(f"  IOInt:  {result.ioint_count} 条")
    print(f"  IOAccess: {result.ioaccess_count} 条")


if __name__ == '__main__':
    main()