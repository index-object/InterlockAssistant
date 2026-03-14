import os
import sys
from src.services.models import init_engine, Base

DB_PATH = 'data/keywords.db'


def init_database(db_path: str = DB_PATH):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    engine = init_engine(db_path)
    print(f"数据库初始化完成: {db_path}")
    return engine


def reset_database(db_path: str = DB_PATH):
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"已删除旧数据库: {db_path}")
    return init_database(db_path)


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--reset':
        reset_database()
    else:
        init_database()