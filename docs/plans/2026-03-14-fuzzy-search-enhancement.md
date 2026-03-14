# 检索功能模糊匹配增强实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 在精准匹配无结果时，使用difflib相似度算法进行模糊搜索，返回最匹配的一个结果。

**Architecture:** 在DatabaseService中新增fuzzy_search_tag_name方法，使用difflib.SequenceMatcher计算输入文本与所有tag_name的相似度，返回超过阈值且相似度最高的结果。修改floating_window.py的update_content方法，在精准匹配失败后调用模糊搜索。

**Tech Stack:** Python 3.x, difflib (内置库), SQLAlchemy

---

## Task 1: 编写模糊搜索单元测试

**Files:**
- Modify: `tests/test_database_service.py`

**Step 1: 编写模糊搜索测试用例**

在 `tests/test_database_service.py` 文件末尾添加测试用例：

```python
import pytest
from difflib import SequenceMatcher


class TestFuzzySearch:
    """模糊搜索功能测试"""

    def test_fuzzy_search_returns_highest_similarity(self, db_service_with_io):
        """测试返回相似度最高的结果"""
        db = db_service_with_io
        
        # 测试：mLZT16103_LL 应匹配到 rLTZ_16103
        result = db.fuzzy_search_tag_name('mLZT16103_LL')
        assert result is not None
        assert 'LTZ_16103' in result.get('tag_name', '')

    def test_fuzzy_search_below_threshold_returns_none(self, db_service_with_io):
        """测试相似度低于阈值时返回None"""
        db = db_service_with_io
        
        # 完全不相关的输入
        result = db.fuzzy_search_tag_name('XYZABC12345')
        assert result is None

    def test_fuzzy_search_exact_match(self, db_service_with_io):
        """测试精确匹配时返回正确结果"""
        db = db_service_with_io
        
        # 先获取一个存在的tag_name
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
```

**Step 2: 添加测试fixture**

在 `tests/test_database_service.py` 文件中添加fixture（如果不存在）：

```python
@pytest.fixture
def db_service_with_io():
    """创建带有测试IO数据的数据库服务"""
    import tempfile
    import os
    from src.services.database_service import DatabaseService
    from src.services.models import IOReal
    
    # 创建临时数据库
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    db = DatabaseService(db_path)
    
    # 插入测试数据
    session = db._get_session()
    try:
        # 添加一些测试IOReal记录
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
    
    yield db
    
    # 清理
    os.unlink(db_path)
```

**Step 3: 运行测试确认失败**

```cmd
uv run pytest tests/test_database_service.py::TestFuzzySearch -v
```

Expected: 测试失败，提示 `fuzzy_search_tag_name` 方法不存在

---

## Task 2: 实现核心标识符提取方法

**Files:**
- Modify: `src/services/database_service.py`

**Step 1: 添加核心标识符提取辅助方法**

在 `extract_core_identifier` 方法之后添加新的辅助方法：

```python
def _normalize_for_comparison(self, tag_name: str) -> str:
    """
    标准化tag_name用于相似度比较
    去除前缀(m/c/d/g/r)和后缀，保留核心部分
    """
    if not tag_name:
        return ''
    
    result = tag_name.lower()
    
    # 去除常见前缀
    for prefix in ['m', 'c', 'd', 'g', 'r']:
        if result.startswith(prefix):
            result = result[1:]
            break
    
    # 去除后缀（如 _LL, _HH, _ALM 等）
    suffixes = ['_ll', '_hh', '_alm', '_sp', '_pv', '_out']
    for suffix in suffixes:
        if result.endswith(suffix):
            result = result[:-len(suffix)]
            break
    
    return result
```

**Step 2: 运行现有测试确保不破坏功能**

```cmd
uv run pytest tests/test_database_service.py -v
```

Expected: 所有现有测试通过

**Step 3: 提交**

```cmd
git add src/services/database_service.py
git commit -m "feat: add _normalize_for_comparison helper method"
```

---

## Task 3: 实现模糊搜索方法

**Files:**
- Modify: `src/services/database_service.py`

**Step 1: 添加导入**

在 `database_service.py` 文件顶部导入区域添加：

```python
from difflib import SequenceMatcher
```

**Step 2: 实现fuzzy_search_tag_name方法**

在 `_normalize_for_comparison` 方法之后添加：

```python
def fuzzy_search_tag_name(self, text: str, threshold: float = 0.7) -> Optional[Dict]:
    """
    使用相似度算法模糊搜索tag_name
    
    Args:
        text: 输入的搜索文本
        threshold: 相似度阈值，默认0.7
        
    Returns:
        相似度最高且超过阈值的结果字典，无匹配返回None
    """
    if not text:
        return None
    
    # 获取所有IOReal记录
    all_records = self.get_all_io_real()
    if not all_records:
        return None
    
    # 标准化输入文本
    normalized_input = self._normalize_for_comparison(text)
    
    best_match = None
    best_ratio = threshold  # 必须超过阈值
    
    for record in all_records:
        tag_name = record.get('tag_name', '')
        if not tag_name:
            continue
        
        # 标准化tag_name
        normalized_tag = self._normalize_for_comparison(tag_name)
        
        # 计算相似度
        ratio = SequenceMatcher(None, normalized_input, normalized_tag).ratio()
        
        # 也计算原始文本的相似度作为补充
        raw_ratio = SequenceMatcher(None, text.lower(), tag_name.lower()).ratio()
        
        # 取两者中较高的值
        final_ratio = max(ratio, raw_ratio)
        
        if final_ratio > best_ratio:
            best_ratio = final_ratio
            best_match = record
    
    return best_match
```

**Step 3: 运行模糊搜索测试**

```cmd
uv run pytest tests/test_database_service.py::TestFuzzySearch -v
```

Expected: 所有测试通过

**Step 4: 提交**

```cmd
git add src/services/database_service.py
git commit -m "feat: implement fuzzy_search_tag_name method"
```

---

## Task 4: 集成到界面

**Files:**
- Modify: `src/ui/floating_window.py`

**Step 1: 修改update_content方法**

将 `update_content` 方法修改为在精准匹配失败后调用模糊搜索：

```python
def update_content(self, text: str):
    self.content_edit.setPlainText(text[:100])
    
    self.result_list.clear()
    
    core_id = self.database_service.extract_core_identifier(text)
    if core_id:
        real_tag = 'r' + core_id
        results = self.database_service.get_all_io_real()
        matched = [r for r in results if core_id in r.get('tag_name', '')]
    else:
        matched = self.database_service.search_io_real(text)
    
    if matched:
        for result in matched:
            self._add_real_result_to_list(result)
    else:
        # 精准匹配无结果，尝试模糊搜索
        fuzzy_result = self.database_service.fuzzy_search_tag_name(text)
        if fuzzy_result:
            self._add_real_result_to_list(fuzzy_result, is_fuzzy=True)
        else:
            self.result_list.addItem("无匹配结果")
            self.result_list.setStyleSheet("""
                QListWidget {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    font-size: 11px;
                    color: #999;
                }
            """)
```

**Step 2: 修改_add_real_result_to_list方法**

添加 `is_fuzzy` 参数以区分精准匹配和模糊匹配：

```python
def _add_real_result_to_list(self, real: Dict, is_fuzzy: bool = False):
    tag_name = real.get('tag_name', '')
    comment = real.get('comment', '')
    eng_units = real.get('eng_units', '')
    min_eu = real.get('min_eu', '')
    max_eu = real.get('max_eu', '')
    item_name = real.get('item_name', '')
    access_name = real.get('access_name', '')
    
    alarm_info = self._get_alarm_info(real)
    
    lines = []
    # 模糊匹配时添加标识
    prefix = "[模糊匹配] " if is_fuzzy else ""
    lines.append(f"{prefix}位号: {tag_name}")
    
    device_name = self.access_name_map.get(access_name, '')
    if device_name:
        lines.append(f"装置: {device_name}")
    
    if comment:
        lines.append(f"注释: {comment}")
    
    unit_range = f"{eng_units}" if eng_units else ""
    if min_eu != '' and max_eu != '':
        unit_range = f"{eng_units} | 量程: {min_eu} ~ {max_eu}" if eng_units else f"量程: {min_eu} ~ {max_eu}"
    elif eng_units:
        unit_range = eng_units
    if unit_range:
        lines.append(unit_range)
    
    if alarm_info:
        lines.append(f"报警: {alarm_info}")
    
    if item_name:
        lines.append(f"访问名: {item_name}")
    
    self.result_list.addItem('\n'.join(lines))
    self.result_list.setStyleSheet("""
        QListWidget {
            background-color: #ecf0f1;
            border: 1px solid #bdc3c7;
            border-radius: 4px;
            font-size: 11px;
        }
        QListWidget::item {
            padding: 4px;
        }
    """)
```

**Step 3: 手动测试**

启动应用，测试模糊搜索功能：

```cmd
uv run python src/main.py
```

测试用例：
- 输入 `mLZT16103_LL`，应显示 `[模糊匹配] 位号: rLTZ_16103`
- 输入精确存在的位号，应正常显示无前缀

**Step 4: 提交**

```cmd
git add src/ui/floating_window.py
git commit -m "feat: integrate fuzzy search into UI with visual indicator"
```

---

## Task 5: 更新设计文档

**Files:**
- Modify: `docs/plans/2026-03-14-fuzzy-search-enhancement-design.md`

**Step 1: 添加实现完成记录**

在设计文档末尾添加：

```markdown
## 实现状态

- [x] Task 1: 单元测试编写
- [x] Task 2: 核心标识符提取方法
- [x] Task 3: 模糊搜索方法实现
- [x] Task 4: 界面集成
- [x] Task 5: 文档更新

## 测试结果

（运行测试后填写）

## 遗留问题

（如有）
```

**Step 2: 提交**

```cmd
git add docs/plans/2026-03-14-fuzzy-search-enhancement-design.md
git commit -m "docs: update design doc with implementation status"
```

---

## 执行完成检查清单

- [ ] 所有单元测试通过
- [ ] 手动测试模糊搜索功能正常
- [ ] 精准匹配功能不受影响
- [ ] 代码无LSP错误
- [ ] 所有更改已提交