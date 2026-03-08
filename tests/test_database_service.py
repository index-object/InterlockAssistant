import pytest
import os
import tempfile
from src.services.database_service import DatabaseService

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    yield path
    os.unlink(path)

def test_database_service_init(temp_db):
    db = DatabaseService(temp_db)
    assert os.path.exists(temp_db)

def test_add_keyword(temp_db):
    db = DatabaseService(temp_db)
    id = db.add_keyword('test', '测试关键词')
    assert id > 0

def test_search_keywords(temp_db):
    db = DatabaseService(temp_db)
    db.add_keyword('test', '测试关键词')
    results = db.search('test')
    assert len(results) > 0
    assert results[0]['keyword'] == 'test'

def test_get_all_keywords(temp_db):
    db = DatabaseService(temp_db)
    db.add_keyword('test1', '测试1')
    db.add_keyword('test2', '测试2')
    keywords = db.get_all_keywords()
    assert len(keywords) >= 2

def test_delete_keyword(temp_db):
    db = DatabaseService(temp_db)
    id = db.add_keyword('delete', '删除')
    db.delete_keyword(id)
    results = db.search('delete')
    assert len(results) == 0