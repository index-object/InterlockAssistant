# 检索功能模糊匹配增强设计

## 概述

增强现有检索功能，在精准匹配无结果时，使用模糊搜索找到一个最匹配的结果显示给用户。

## 需求分析

### 当前问题

当前检索功能通过字符串精准匹配（LIKE `%text%`）实现检索。当用户输入的位号格式与数据库中存储的格式不完全一致时，无法找到结果。

**示例**：
- 输入：`mLZT16103_LL`
- 期望匹配：`rLTZ_16103`
- 当前结果：无匹配

### 需求确认

| 项目 | 说明 |
|------|------|
| 匹配字段 | 仅 `tag_name`（位号） |
| 结果数量 | 显示相似度最高的1个结果 |
| 算法选择 | Python 内置 `difflib.SequenceMatcher` |
| 相似度阈值 | 70% |

## 实现方案

### 修改文件

`src/services/database_service.py`

### 新增方法

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
```

### 核心逻辑

1. **提取核心标识**：去除位号前缀（m/c/d/g/r等），提取核心部分
2. **遍历匹配**：遍历所有IOReal记录，计算输入与每个tag_name的相似度
3. **阈值过滤**：只保留相似度超过阈值的结果
4. **最佳匹配**：返回相似度最高的结果

### 相似度计算

使用 `difflib.SequenceMatcher.ratio()` 计算相似度：
- 返回值范围 [0, 1]
- 1 表示完全相同
- 0 表示完全不同

## 匹配流程

```
输入文本 mLZT16103_LL
       ↓
提取核心标识 LZT16103 (去除前缀m)
       ↓
精准匹配 → 无结果
       ↓
模糊匹配 → 遍历所有tag_name
       ↓
计算相似度: rLTZ_16103 相似度 0.85 (>0.7)
       ↓
返回 rLTZ_16103 记录
```

## 界面集成

修改 `src/ui/floating_window.py` 的 `update_content()` 方法：
1. 先执行现有的精准匹配逻辑
2. 若无结果，调用 `fuzzy_search_tag_name()` 进行模糊匹配
3. 显示模糊匹配结果（可选：添加视觉提示区分精准/模糊匹配）

## 测试计划

1. **精准匹配测试**：确保现有精准匹配功能不受影响
2. **模糊匹配测试**：
   - `mLZT16103_LL` → `rLTZ_16103`
   - `mPLC1_100A` → `rPLC1_100A`
   - 不完整输入测试
3. **阈值测试**：验证70%阈值合理性
4. **无匹配测试**：验证完全无匹配时的处理

## 不涉及内容

- 不修改数据库结构
- 不修改CSV导入逻辑
- 不添加新的第三方依赖

## 实现状态

- [x] Task 1: 单元测试编写
- [x] Task 2: 核心标识符提取方法
- [x] Task 3: 模糊搜索方法实现
- [x] Task 4: 界面集成
- [x] Task 5: 文档更新

## 测试结果

所有单元测试通过：
- test_fuzzy_search_returns_highest_similarity: PASSED
- test_fuzzy_search_below_threshold_returns_none: PASSED
- test_fuzzy_search_exact_match: PASSED
- test_fuzzy_search_empty_input: PASSED

## 实现说明

1. 使用 `difflib.SequenceMatcher` 计算相似度
2. 阈值设为 0.7（70%）
3. 双重比较策略：标准化后比较 + 原始文本比较，取较高值
4. 界面集成：精准匹配无结果时自动调用模糊搜索
5. 模糊匹配结果显示 "[模糊匹配]" 前缀标识

## 遗留问题

无