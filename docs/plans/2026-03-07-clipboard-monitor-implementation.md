# 剪贴板监视助手 - 实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 实现一个Windows剪贴板监视工具，具备窗口来源显示、过滤、检索和快捷键功能

**Architecture:** 使用PySide2构建GUI，pyclipboard监控剪贴板，win32gui获取窗口信息，SQLite存储检索关键词

**Tech Stack:** Python 3.8+, PySide2, pyclipboard, win32gui, QHotkey, SQLite

---

## Task 1: 项目初始化

**Files:**
- Create: `requirements.txt`
- Create: `src/main.py`
- Create: `config.json`
- Create: `data/keywords.db`

**Step 1: 创建 requirements.txt**

```txt
PySide2==5.15.2
pyclipboard==1.0.2
pywin32==306
QHotkey==0.0.7
```

**Step 2: 创建 config.json**

```json
{
    "hotkeys": {
        "show_hide": "Ctrl+Shift+V"
    },
    "window_filters": [],
    "ui": {
        "opacity": 0.9,
        "position": "right-bottom"
    }
}
```

**Step 3: 创建 SQLite 数据库**

```python
import sqlite3

conn = sqlite3.connect('data/keywords.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS keywords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        keyword TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()
conn.close()
```

**Step 4: 提交**

```bash
git init
git add requirements.txt config.json data/
git commit -m "chore: 初始化项目结构"
```

---

## Task 2: 核心服务层 - 剪贴板监控

**Files:**
- Create: `src/services/clipboard_watcher.py`
- Test: `tests/test_clipboard_watcher.py`

**Step 1: 编写测试**

```python
import pytest
from src.services.clipboard_watcher import ClipboardWatcher

def test_clipboard_watcher_init():
    watcher = ClipboardWatcher()
    assert watcher is not None
    assert watcher.last_content == ""
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_clipboard_watcher.py -v
```

**Step 3: 实现 ClipboardWatcher**

```python
import pyclipboard
import threading
import time

class ClipboardWatcher:
    def __init__(self):
        self.last_content = ""
        self.callback = None
        self._running = False
        self._thread = None
    
    def start(self, callback=None):
        self.callback = callback
        self._running = True
        self._thread = threading.Thread(target=self._watch)
        self._thread.daemon = True
        self._thread.start()
    
    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()
    
    def _watch(self):
        while self._running:
            try:
                current = pyclipboard.paste()
                if current != self.last_content and current:
                    self.last_content = current
                    if self.callback:
                        self.callback(current)
            except:
                pass
            time.sleep(0.5)
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_clipboard_watcher.py -v
```

**Step 5: 提交**

```bash
git add src/services/clipboard_watcher.py tests/test_clipboard_watcher.py
git commit -m "feat: 添加剪贴板监控服务"
```

---

## Task 3: 核心服务层 - 窗口信息获取

**Files:**
- Create: `src/services/window_info.py`
- Test: `tests/test_window_info.py`

**Step 1: 编写测试**

```python
import pytest
from src.services.window_info import WindowInfo

def test_get_foreground_window():
    info = WindowInfo()
    hwnd = info.get_foreground_window()
    assert hwnd is not None
    assert hwnd > 0

def test_get_window_title():
    info = WindowInfo()
    title = info.get_window_title()
    assert isinstance(title, str)
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_window_info.py -v
```

**Step 3: 实现 WindowInfo**

```python
import ctypes
from ctypes import wintypes

class WindowInfo:
    def __init__(self):
        self.user32 = ctypes.windll.user32
    
    def get_foreground_window(self):
        return self.user32.GetForegroundWindow()
    
    def get_window_text(self, hwnd=None):
        if hwnd is None:
            hwnd = self.get_foreground_window()
        length = self.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value
    
    def get_window_title(self):
        return self.get_window_text()
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_window_info.py -v
```

**Step 5: 提交**

```bash
git add src/services/window_info.py tests/test_window_info.py
git commit -m "feat: 添加窗口信息获取服务"
```

---

## Task 4: 核心服务层 - 数据库检索

**Files:**
- Create: `src/services/database_service.py`
- Test: `tests/test_database_service.py`

**Step 1: 编写测试**

```python
import pytest
import os
from src.services.database_service import DatabaseService

def test_search_keywords():
    db = DatabaseService('data/keywords.db')
    db.add_keyword('test', '测试关键词')
    results = db.search('test')
    assert len(results) > 0
    assert results[0]['keyword'] == 'test'
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_database_service.py -v
```

**Step 3: 实现 DatabaseService**

```python
import sqlite3
from typing import List, Dict

class DatabaseService:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._init_db()
    
    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def add_keyword(self, keyword: str, description: str = "") -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO keywords (keyword, description) VALUES (?, ?)",
            (keyword, description)
        )
        conn.commit()
        result = cursor.lastrowid
        conn.close()
        return result
    
    def search(self, text: str) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM keywords WHERE keyword LIKE ?",
            (f'%{text}%',)
        )
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
    
    def delete_keyword(self, keyword_id: int):
        conn = sqlite3.connect(self.db_path)
        conn.execute("DELETE FROM keywords WHERE id = ?", (keyword_id,))
        conn.commit()
        conn.close()
    
    def get_all_keywords(self) -> List[Dict]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM keywords")
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return results
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_database_service.py -v
```

**Step 5: 提交**

```bash
git add src/services/database_service.py tests/test_database_service.py
git commit -m "feat: 添加数据库检索服务"
```

---

## Task 5: 核心服务层 - 快捷键管理

**Files:**
- Create: `src/services/hotkey_manager.py`
- Test: `tests/test_hotkey_manager.py`

**Step 1: 编写测试**

```python
import pytest
from src.services.hotkey_manager import HotkeyManager

def test_hotkey_manager_init():
    manager = HotkeyManager()
    assert manager is not None
```

**Step 2: 运行测试验证失败**

```bash
pytest tests/test_hotkey_manager.py -v
```

**Step 3: 实现 HotkeyManager**

```python
from QHotkey import QHotkey, QKeySequence, Qt
import json

class HotkeyManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.hotkeys = {}
        self.load_config()
    
    def load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.hotkeys = config.get('hotkeys', {})
        except FileNotFoundError:
            self.hotkeys = {'show_hide': 'Ctrl+Shift+V'}
    
    def save_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        config['hotkeys'] = self.hotkeys
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    def set_hotkey(self, name: str, hotkey: str):
        self.hotkeys[name] = hotkey
        self.save_config()
    
    def get_hotkey(self, name: str) -> str:
        return self.hotkeys.get(name, 'Ctrl+Shift+V')
```

**Step 4: 运行测试验证通过**

```bash
pytest tests/test_hotkey_manager.py -v
```

**Step 5: 提交**

```bash
git add src/services/hotkey_manager.py tests/test_hotkey_manager.py
git commit -m "feat: 添加快捷键管理服务"
```

---

## Task 6: UI层 - 悬浮窗

**Files:**
- Create: `src/ui/floating_window.py`
- Modify: `src/main.py`

**Step 1: 创建悬浮窗 UI**

```python
from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QListWidget
from PySide2.QtCore import Qt, QTimer
from PySide2.QtGui import QClipboard

class FloatingWindow(QWidget):
    def __init__(self, clipboard_watcher, window_info, database_service):
        super().__init__()
        self.clipboard_watcher = clipboard_watcher
        self.window_info = window_info
        self.database_service = database_service
        self.init_ui()
        self.connect_signals()
    
    def init_ui(self):
        self.setWindowTitle("剪贴板监视")
        self.setFixedSize(300, 180)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 标题栏
        title_layout = QHBoxLayout()
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(30, 25)
        self.copy_btn.setToolTip("复制窗口来源")
        
        self.title_label = QLabel("等待剪贴板...")
        self.title_label.setStyleSheet("font-weight: bold;")
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(25, 25)
        
        title_layout.addWidget(self.copy_btn)
        title_layout.addWidget(self.title_label)
        title_layout.addStretch()
        title_layout.addWidget(self.close_btn)
        
        # 剪贴板内容
        self.content_label = QLabel("剪贴板内容:")
        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(True)
        self.content_edit.setMaximumHeight(50)
        
        # 检索结果
        self.search_label = QLabel("检索结果:")
        self.result_list = QListWidget()
        
        layout.addLayout(title_layout)
        layout.addWidget(self.content_label)
        layout.addWidget(self.content_edit)
        layout.addWidget(self.search_label)
        layout.addWidget(self.result_list)
        
        self.setLayout(layout)
        self.apply_style()
    
    def apply_style(self):
        self.setStyleSheet("""
            QWidget {
                background-color: rgba(240, 240, 240, 230);
                border-radius: 8px;
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: rgba(200, 200, 200, 150);
                border-radius: 4px;
            }
            QTextEdit, QListWidget {
                background-color: rgba(255, 255, 255, 200);
                border: 1px solid #ddd;
                border-radius: 4px;
            }
        """)
    
    def connect_signals(self):
        self.close_btn.clicked.connect(self.hide_to_tray)
        self.copy_btn.clicked.connect(self.copy_window_title)
    
    def hide_to_tray(self):
        self.hide()
    
    def copy_window_title(self):
        title = self.title_label.text()
        if title and title != "等待剪贴板...":
            clipboard = QClipboard()
            clipboard.setText(title)
    
    def update_content(self, text: str):
        self.content_edit.setPlainText(text[:100])
        # 执行检索
        results = self.database_service.search(text)
        self.result_list.clear()
        for result in results:
            self.result_list.addItem(f"{result['keyword']} → {result.get('description', '')}")
    
    def update_title(self, title: str):
        if title:
            self.title_label.setText(title)
        else:
            self.title_label.setText("未知窗口")
    
    def move_to_corner(self):
        from PySide2.QtWidgets import QDesktopWidget
        screen = QDesktopWidget().screenGeometry()
        self.move(screen.width() - self.width() - 20, screen.height() - self.height() - 60)
```

**Step 2: 更新 main.py**

```python
import sys
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide2.QtCore import Qt
from PySide2.QtGui import QIcon
from src.services.clipboard_watcher import ClipboardWatcher
from src.services.window_info import WindowInfo
from src.services.database_service import DatabaseService
from src.services.hotkey_manager import HotkeyManager
from src.ui.floating_window import FloatingWindow

class ClipboardMonitorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        # 初始化服务
        self.clipboard_watcher = ClipboardWatcher()
        self.window_info = WindowInfo()
        self.database_service = DatabaseService('data/keywords.db')
        self.hotkey_manager = HotkeyManager()
        
        # 创建悬浮窗
        self.floating_window = FloatingWindow(
            self.clipboard_watcher,
            self.window_info,
            self.database_service
        )
        self.floating_window.move_to_corner()
        
        # 创建托盘
        self.create_tray()
        
        # 启动剪贴板监控
        self.clipboard_watcher.start(self.on_clipboard_change)
        
        self.floating_window.show()
    
    def create_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("剪贴板监视")
        
        menu = QMenu()
        menu.addAction("显示/隐藏", self.toggle_window)
        menu.addAction("退出", self.quit_app)
        self.tray.setContextMenu(menu)
        
        self.tray.activated.connect(self.toggle_window)
        self.tray.show()
    
    def toggle_window(self):
        if self.floating_window.isVisible():
            self.floating_window.hide()
        else:
            self.floating_window.show()
    
    def on_clipboard_change(self, text):
        title = self.window_info.get_window_title()
        self.floating_window.update_title(title)
        self.floating_window.update_content(text)
    
    def quit_app(self):
        self.clipboard_watcher.stop()
        self.app.quit()
    
    def run(self):
        sys.exit(self.app.exec_())

if __name__ == "__main__":
    app = ClipboardMonitorApp()
    app.run()
```

**Step 3: 提交**

```bash
git add src/ui/floating_window.py src/main.py
git commit -m "feat: 实现悬浮窗UI"
```

---

## Task 7: UI层 - 配置窗口

**Files:**
- Create: `src/ui/config_window.py`
- Modify: `src/main.py`

**Step 1: 创建配置窗口**

```python
from PySide2.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QPushButton, QLineEdit, QGroupBox, QCheckBox
from PySide2.QtCore import Qt
import json

class ConfigWindow(QDialog):
    def __init__(self, database_service, hotkey_manager, parent=None):
        super().__init__(parent)
        self.database_service = database_service
        self.hotkey_manager = hotkey_manager
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle("配置")
        self.setMinimumSize(400, 350)
        
        layout = QVBoxLayout()
        
        # 快捷键设置
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QVBoxLayout()
        hotkey_layout.addWidget(QLabel("显示/隐藏:"))
        self.hotkey_edit = QLineEdit()
        hotkey_layout.addWidget(self.hotkey_edit)
        hotkey_group.setLayout(hotkey_layout)
        
        # 窗口过滤
        filter_group = QGroupBox("窗口过滤")
        filter_layout = QVBoxLayout()
        self.filter_list = QListWidget()
        self.filter_list.setSelectionMode(QListWidget.MultiSelection)
        filter_layout.addWidget(self.filter_list)
        filter_btn_layout = QHBoxLayout()
        filter_btn_layout.addWidget(QPushButton("刷新窗口"))
        filter_btn_layout.addWidget(QPushButton("清除"))
        filter_layout.addLayout(filter_btn_layout)
        filter_group.setLayout(filter_layout)
        
        # 关键词管理
        keyword_group = QGroupBox("关键词管理")
        keyword_layout = QVBoxLayout()
        self.keyword_list = QListWidget()
        keyword_input_layout = QHBoxLayout()
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("输入关键词")
        keyword_input_layout.addWidget(self.keyword_edit)
        keyword_input_layout.addWidget(QPushButton("添加"))
        keyword_layout.addWidget(self.keyword_list)
        keyword_layout.addLayout(keyword_input_layout)
        keyword_group.setLayout(keyword_layout)
        
        # 按钮
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("保存")
        cancel_btn = QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addWidget(hotkey_group)
        layout.addWidget(filter_group)
        layout.addWidget(keyword_group)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        save_btn.clicked.connect(self.save_config)
        cancel_btn.clicked.connect(self.reject)
    
    def load_data(self):
        # 加载快捷键
        self.hotkey_edit.setText(self.hotkey_manager.get_hotkey('show_hide'))
        
        # 加载关键词
        keywords = self.database_service.get_all_keywords()
        for kw in keywords:
            self.keyword_list.addItem(f"{kw['keyword']} - {kw.get('description', '')}")
        
        # 加载过滤窗口
        self.load_window_filters()
    
    def load_window_filters(self):
        import ctypes
        from ctypes import wintypes
        
        self.filter_list.clear()
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        
        self.windows = []
        
        def callback(hwnd, lParam):
            if hwnd:
                length = GetWindowTextLength(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buffer, length + 1)
                    title = buffer.value
                    if title and title not in self.windows:
                        self.windows.append(title)
            return True
        
        EnumWindows(EnumWindowsProc(callback), 0)
        
        # 加载已保存的过滤配置
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                saved_filters = config.get('window_filters', [])
        except:
            saved_filters = []
        
        for title in self.windows:
            item = QListWidgetItem(title)
            item.setCheckState(Qt.Checked if title in saved_filters else Qt.Unchecked)
            self.filter_list.addItem(item)
    
    def save_config(self):
        # 保存快捷键
        hotkey = self.hotkey_edit.text()
        self.hotkey_manager.set_hotkey('show_hide', hotkey)
        
        # 保存过滤窗口
        filters = []
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            if item.checkState() == Qt.Checked:
                filters.append(item.text())
        
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        config['window_filters'] = filters
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        self.accept()
```

**Step 2: 更新 main.py 添加配置窗口**

在托盘菜单中添加配置入口:

```python
menu.addAction("配置", self.open_config)

def open_config(self):
    from src.ui.config_window import ConfigWindow
    config = ConfigWindow(self.database_service, self.hotkey_manager)
    config.exec_()
```

**Step 3: 提交**

```bash
git add src/ui/config_window.py
git commit -m "feat: 添加配置窗口"
```

---

## Task 8: 完善快捷键功能

**Files:**
- Modify: `src/main.py`

**Step 1: 添加全局热键支持**

```python
from PySide2.QtWidgets import QShortcut
from PySide2.QtGui import QKeySequence

# 在 ClipboardMonitorApp.__init__ 中添加
self.show_hide_shortcut = QShortcut(
    QKeySequence(self.hotkey_manager.get_hotkey('show_hide')),
    self.floating_window
)
self.show_hide_shortcut.activated.connect(self.toggle_window)
```

**Step 2: 提交**

```bash
git add src/main.py
git commit -m "feat: 添加全局快捷键支持"
```

---

## Task 9: 窗口过滤功能

**Files:**
- Modify: `src/services/window_info.py`
- Modify: `src/main.py`

**Step 1: 添加过滤检查方法**

```python
# 在 WindowInfo 类中添加
def should_monitor(self, filters: list) -> bool:
    if not filters:
        return True
    title = self.get_window_text()
    for f in filters:
        if f in title:
            return True
    return False
```

**Step 2: 在回调中应用过滤**

```python
def on_clipboard_change(self, text):
    # 加载过滤配置
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            filters = config.get('window_filters', [])
    except:
        filters = []
    
    if self.window_info.should_monitor(filters):
        title = self.window_info.get_window_title()
        self.floating_window.update_title(title)
        self.floating_window.update_content(text)
```

**Step 3: 提交**

```bash
git add src/services/window_info.py src/main.py
git commit -m "feat: 添加窗口过滤功能"
```

---

## Task 10: 整合测试与最终调整

**Files:**
- Modify: 调整UI样式和交互

**Step 1: 运行完整测试**

```bash
pytest tests/ -v
```

**Step 2: 手动测试功能**

```bash
python src/main.py
```

**Step 3: 提交**

```bash
git add .
git commit -m "feat: 完成所有功能开发"
```

---

## 实施选择

**计划已完成并保存到 `docs/plans/2026-03-07-clipboard-monitor-implementation.md`。两种执行方式:**

1. **子代理驱动 (本会话)** - 我为每个任务分派新的子代理，任务间进行代码审查，快速迭代

2. **并行会话 (单独)** - 在新会话中使用executing-plans，批量执行并设置检查点

**请选择哪种方式?**