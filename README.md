# InterlockAssistant - Windows剪贴板监视助手

Windows系统剪贴板监视工具，可显示剪贴板内容来源窗口，支持过滤、检索和快捷键操作。

## 功能特性

- 实时监控剪贴板变化（仅文本内容）
- 显示剪贴板内容来源窗口
- 置顶悬浮窗，支持快捷键显示/隐藏
- 自定义窗口过滤（只监控指定软件）
- SQLite数据库关键词检索
- 系统托盘支持（最小化到托盘）
- 复制窗口来源功能
- 可自定义快捷键

## 技术栈

- Python 3.8
- PySide2 5.15.2
- pywin32
- SQLite
- uv (包管理)

## 项目结构

```
InterlockAssistant/
├── src/
│   ├── main.py              # 主程序入口
│   ├── services/
│   │   ├── clipboard_watcher.py  # 剪贴板监控
│   │   ├── database_service.py   # 数据库服务
│   │   ├── hotkey_manager.py     # 快捷键管理
│   │   └── window_info.py        # 窗口信息获取
│   └── ui/
│       ├── floating_window.py    # 悬浮窗UI
│       └── config_window.py      # 配置窗口
├── tests/                   # 单元测试
├── data/keywords.db        # SQLite数据库
├── config.json            # 配置文件
├── pyproject.toml         # 项目配置
├── .python-version        # Python版本
└── run.bat               # Windows启动脚本
```

## 安装与运行

### 前置要求

- 安装 [uv](https://docs.astral.sh/uv/)

### 快速开始

```bash
# 安装依赖并运行
uv sync
uv run python -m src.main

# 或使用启动脚本
run.bat
```

### 运行测试

```bash
uv run pytest tests/ -v
```

## 使用说明

### 默认快捷键

- `Ctrl+Shift+V`: 显示/隐藏悬浮窗

### 悬浮窗功能

- 显示当前剪贴板内容来源窗口
- 显示剪贴板文本预览
- 显示数据库检索结果
- 点击 📋 按钮复制窗口来源
- 点击 × 按钮最小化到托盘

### 配置窗口

- 快捷键设置
- 窗口过滤（勾选要监控的软件）
- 关键词管理（添加/查看检索关键词）

### 系统托盘

- 单击托盘图标：显示/隐藏窗口
- 右键托盘图标：菜单操作

## 配置文件

`config.json` 示例:

```json
{
    "hotkeys": {
        "show_hide": "Ctrl+Shift+V"
    },
    "window_filters": [
        "Notepad++",
        "Visual Studio Code"
    ],
    "ui": {
        "opacity": 0.9,
        "position": "right-bottom"
    }
}
```

## 开发

### 添加新依赖

```bash
uv add package-name
```

### 添加开发依赖

```bash
uv add --dev package-name
```

## License

MIT