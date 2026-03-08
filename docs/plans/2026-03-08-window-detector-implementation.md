# 窗口信息检测器实现计划

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 开发一个独立的窗口检测/选择工具，用于收集目标窗口的详细信息

**Architecture:** 使用UI Automation API获取窗口控件树，新建检测器窗口显示信息

**Tech Stack:** PySide2, uiautomation, pywin32

---

## Task 1: 添加 uiautomation 依赖

**Files:**
- Modify: `pyproject.toml:11`

**Step 1: 添加依赖**

在 pyproject.toml 的 dependencies 中添加 `"uiautomation>=2.0.8"`

**Step 2: 安装依赖**

```bash
cd G:\work\python\InterlockAssistant && uv add uiautomation
```

**Step 3: 验证安装**

```bash
uv pip list | findstr uiautomation
```

---

## Task 2: 创建窗口信息检测器类

**Files:**
- Create: `src/services/window_detector.py`

**Step 1: 创建测试文件**

```python
# tests/test_window_detector.py
import pytest
from src.services.window_detector import WindowDetector

def test_window_detector_init():
    detector = WindowDetector()
    assert detector is not None
```

**Step 2: 创建实现**

```python
import logging
import ctypes
from ctypes import wintypes
from PySide2.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class WindowDetector(QObject):
    window_selected = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self._target_hwnd = None
    
    def get_window_info(self, hwnd):
        info = {
            'hwnd': hwnd,
            'class_name': self._get_class_name(hwnd),
            'title': self._get_title(hwnd),
            'process_name': self._get_process_name(hwnd),
            'process_id': self._get_process_id(hwnd),
        }
        return info
    
    def get_control_tree(self, hwnd):
        # TODO: 使用 uiautomation 获取控件树
        return []
    
    def _get_class_name(self, hwnd):
        try:
            buf = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(hwnd, buf, 256)
            return buf.value
        except:
            return ""
    
    def _get_title(self, hwnd):
        try:
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return ""
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value
        except:
            return ""
    
    def _get_process_id(self, hwnd):
        try:
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            return pid.value
        except:
            return 0
    
    def _get_process_name(self, hwnd):
        try:
            pid = self._get_process_id(hwnd)
            if pid:
                import psutil
                return psutil.Process(pid).name()
        except:
            pass
        return ""
```

**Step 3: 运行测试**

```bash
pytest tests/test_window_detector.py -v
```

---

## Task 3: 创建窗口检测器UI

**Files:**
- Create: `src/ui/window_detector_window.py`

**Step 1: 创建UI类**

```python
from PySide2.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QTextEdit, QTreeWidget, QTreeWidgetItem)
from PySide2.QtCore import Qt

class WindowDetectorWindow(QWidget):
    def __init__(self, window_detector, window_picker):
        super().__init__()
        self.window_detector = window_detector
        self.window_picker = window_picker
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("窗口信息检测器")
        self.setFixedSize(600, 500)
        
        layout = QVBoxLayout(self)
        
        # 按钮行
        btn_layout = QHBoxLayout()
        
        self.pick_btn = QPushButton("开始选择")
        self.pick_btn.clicked.connect(self.start_pick)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.clicked.connect(self.refresh_info)
        
        self.save_btn = QPushButton("保存目标")
        self.save_btn.clicked.connect(self.save_target)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.pick_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        # 窗口基本信息
        self.info_label = QLabel("窗口信息:")
        layout.addWidget(self.info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(120)
        layout.addWidget(self.info_text)
        
        # 控件树
        self.tree_label = QLabel("控件树:")
        layout.addWidget(self.tree_label)
        
        self.control_tree = QTreeWidget()
        self.control_tree.setHeaderLabels(["类型", "类名", "名称"])
        layout.addWidget(self.control_tree)
    
    def start_pick(self):
        self.window_picker.pick_window(self.on_window_picked)
    
    def on_window_picked(self, window_data):
        # TODO: 处理窗口选择结果
        pass
    
    def refresh_info(self):
        # TODO: 刷新信息
        pass
    
    def save_target(self):
        # TODO: 保存目标
        pass
```

---

## Task 4: 重构窗口选择器

**Files:**
- Modify: `src/services/window_picker.py`

**Step 1: 添加获取进程信息功能**

修改 window_picker.py，支持返回进程信息（已有类名和标题）

**Step 2: 添加信号支持**

添加 QSignal 在选择完成时发送信号

**Step 3: 测试选择功能**

```bash
# 手动测试选择功能
```

---

## Task 5: 集成到主程序

**Files:**
- Modify: `src/main.py`

**Step 1: 添加导入**

```python
from src.services.window_detector import WindowDetector
from src.services.window_picker import WindowPicker
from src.ui.window_detector_window import WindowDetectorWindow
```

**Step 2: 添加菜单项**

在托盘菜单添加"窗口检测器"选项

---

## Task 6: 实现控件树获取功能

**Files:**
- Modify: `src/services/window_detector.py`

**Step 1: 添加 uiautomation 集成**

使用 uiautomation 获取窗口控件树

**Step 2: 填充控件树UI**

在 WindowDetectorWindow 中显示控件树

---

## Task 7: 保存目标配置

**Files:**
- Modify: `src/services/window_detector.py`
- Modify: `src/ui/window_detector_window.py`
- Modify: `config.json`

**Step 1: 实现保存功能**

保存目标窗口信息到 config.json

**Step 2: 验证保存**

读取 config.json 确认保存成功