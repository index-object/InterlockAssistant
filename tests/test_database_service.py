import pytest
import tempfile
import os

from src.services.database_service import DatabaseService
from src.services.models import IOReal


@pytest.fixture
def db_service_with_io():
    """创建带有测试IO数据的数据库服务"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name

    db = DatabaseService(db_path)

    session = db._get_session()
    try:
        test_records = [
            IOReal(tag_name='rLTZ_16103', comment='测试位号1'),
            IOReal(tag_name='rPLC1_100A', comment='测试位号2'),
            IOReal(tag_name='rTT_2001', comment='温度变送器'),
            IOReal(tag_name='mPT_3001', comment='压力变送器'),
        ]
        session.add_all(test_records)
        session.commit()
    finally:
        session.close()

    try:
        yield db
    finally:
        db.engine.dispose()
        if os.path.exists(db_path):
            os.unlink(db_path)


class TestFuzzySearch:
    """模糊搜索功能测试"""

    def test_fuzzy_search_returns_highest_similarity(self, db_service_with_io):
        """测试返回相似度最高的结果"""
        db = db_service_with_io

        result = db.fuzzy_search_tag_name('mLZT16103_LL')
        assert result is not None
        assert 'LTZ_16103' in result.get('tag_name', '')

    def test_fuzzy_search_below_threshold_returns_none(self, db_service_with_io):
        """测试相似度低于阈值时返回None"""
        db = db_service_with_io

        result = db.fuzzy_search_tag_name('XYZABC12345')
        assert result is None

    def test_fuzzy_search_exact_match(self, db_service_with_io):
        """测试精确匹配时返回正确结果"""
        db = db_service_with_io

        all_real = db.get_all_io_real()
        if all_real:
            existing_tag = all_real[0]['tag_name']
            result = db.fuzzy_search_tag_name(existing_tag)
            assert result is not None
            assert result['tag_name'] == existing_tag

    def test_fuzzy_search_empty_input(self, db_service_with_io):
        """测试空输入返回None"""
        db = db_service_with_io

        result = db.fuzzy_search_tag_name('')
        assert result is None

        result = db.fuzzy_search_tag_name(None)
        assert result is None