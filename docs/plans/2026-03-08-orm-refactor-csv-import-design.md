# ORM重构与CSV部分列导入设计文档

## 1. 概述

本设计文档描述了使用 SQLAlchemy ORM 重构数据库管理，并实现从 CSV 文件选择性导入部分列数据的功能。

## 2. 背景

当前项目使用原始 `sqlite3` 库直接操作数据库，存在以下问题：
- SQL 语句分散在代码各处，难以维护
- 缺乏类型安全检查
- 数据模型与数据库表结构耦合度高

## 3. 目标

1. 使用 SQLAlchemy ORM 重构数据库层
2. 实现从 CSV 导入指定列的功能
3. 保持现有 API 兼容性

## 4. 技术选型

- **ORM框架**: SQLAlchemy 2.0
- **数据库**: SQLite
- **CSV解析**: Python csv 模块

## 5. 数据模型设计

### 5.1 IODisc (离散量标签)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| tag_name | String | 标签名称 |
| group_name | String | 分组名称 |
| comment | String | 注释 |
| logged | String | 是否记录 |
| event_logged | String | 事件记录 |
| event_logging_priority | Integer | 事件优先级 |
| retentive_value | String | 保持值 |
| initial_disc | String | 初始离散值 |
| off_msg | String | 关闭消息 |
| on_msg | String | 打开消息 |
| alarm_state | String | 报警状态 |
| alarm_pri | Integer | 报警优先级 |
| d_conversion | String | 转换方式 |
| access_name | String | 访问名称 |
| item_use_tagname | String | 使用标签名 |
| item_name | String | 项目名称 |
| read_only | String | 只读 |
| alarm_comment | String | 报警注释 |
| alarm_ack_model | Integer | 确认模式 |
| dsc_alarm_disable | Integer | 报警禁用 |
| dsc_alarm_inhibitor | Integer | 报警抑制器 |
| symbolic_name | String | 符号名称 |
| created_at | DateTime | 创建时间 |

### 5.2 IOReal (模拟量标签)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| tag_name | String | 标签名称 |
| comment | String | 注释 |
| eng_units | String | 工程单位 |
| min_eu | Float | 最小工程值 |
| max_eu | Float | 最大工程值 |
| lolo_alarm_state | String | 低低报警状态 |
| lolo_alarm_value | Float | 低低报警值 |
| lolo_alarm_pri | Integer | 低低报警优先级 |
| lo_alarm_state | String | 低报警状态 |
| lo_alarm_value | Float | 低报警值 |
| lo_alarm_pri | Integer | 低报警优先级 |
| hi_alarm_state | String | 高报警状态 |
| hi_alarm_value | Float | 高报警值 |
| hi_alarm_pri | Integer | 高报警优先级 |
| hihi_alarm_state | String | 高高报警状态 |
| hihi_alarm_value | Float | 高高报警值 |
| hihi_alarm_pri | Integer | 高高报警优先级 |
| access_name | String | 访问名称 |
| item_name | String | 项目名称 |
| created_at | DateTime | 创建时间 |

### 5.3 IOAccess (IO访问配置)

| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键，自增 |
| access_name | String | 访问名称 |
| application | String | 应用程序 |
| topic | String | 主题 |
| advise_active | String | 主动建议 |
| dde_protocol | String | DDE协议 |
| sec_application | String | 备用应用程序 |
| sec_topic | String | 备用主题 |
| sec_advise_active | String | 备用主动建议 |
| sec_dde_protocol | String | 备用DDE协议 |
| created_at | DateTime | 创建时间 |

## 6. CSV导入设计

### 6.1 支持的CSV区块

- `IODisc`: 离散量标签
- `IOReal`: 模拟量标签
- `IOAccess`: IO访问配置
- `IOInt`: 整型标签

### 6.2 部分列导入规则

根据需求，只导入以下列：

**IODisc**:
- tag_name, comment, access_name, item_name

**IOReal**:
- tag_name, comment, eng_units, min_eu, max_eu
- lolo_alarm_state, lolo_alarm_value, lolo_alarm_pri
- lo_alarm_state, lo_alarm_value, lo_alarm_pri
- hi_alarm_state, hi_alarm_value, hi_alarm_pri
- hihi_alarm_state, hihi_alarm_value, hihi_alarm_pri
- access_name, item_name

### 6.3 导入模式

- **覆盖模式**: 先清空表，再导入数据
- **增量模式**: 只导入不存在的记录

## 7. 架构设计

```
src/services/
├── __init__.py
├── models.py          # SQLAlchemy模型定义
├── database_service.py # 数据库服务(使用ORM)
└── csv_importer.py    # CSV导入器
```

## 8. API设计

### DatabaseService 类

保持现有方法签名不变：

```python
class DatabaseService:
    def __init__(self, db_path: str = "data/keywords.db")
    def search_io_disc(self, text: str) -> List[Dict]
    def search_io_real(self, text: str) -> List[Dict]
    def get_all_io_disc(self) -> List[Dict]
    def get_all_io_real(self) -> List[Dict]
    def get_io_disc_by_tagname(self, tag_name: str) -> Optional[Dict]
    def get_io_real_by_tagname(self, tag_name: str) -> Optional[Dict]
    def search_all_io_tags(self, text: str) -> List[Dict]
    def find_matching_io_real(self, disc_tag_name: str) -> Optional[Dict]
```

### CSVImporter 类

```python
class CSVImporter:
    def __init__(self, db_service: DatabaseService)
    def import_from_csv(self, csv_path: str, mode: str = "replace") -> ImportResult
    def import_iodisc(self, data: List[Dict], mode: str = "replace") -> int
    def import_ioreal(self, data: List[Dict], mode: str = "replace") -> int
```

## 9. 迁移计划

1. 创建 `models.py` - 定义 SQLAlchemy 模型
2. 重构 `database_service.py` - 使用 ORM 查询
3. 创建 `csv_importer.py` - 实现 CSV 导入功能
4. 更新测试 - 确保功能正常

## 10. 风险与注意事项

- 保持向后兼容，现有调用代码无需修改
- 确保事务正确处理，避免数据不一致
- CSV 编码为 GBK，需正确处理中文
