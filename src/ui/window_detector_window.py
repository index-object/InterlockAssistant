import json
import logging
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                QPushButton, QTextEdit, QTreeWidget, QTreeWidgetItem,
                                QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QClipboard

logger = logging.getLogger(__name__)


class WindowDetectorWindow(QWidget):
    def __init__(self, window_detector, window_picker):
        logger.info("WindowDetectorWindow: 开始初始化...")
        super().__init__()
        logger.info("WindowDetectorWindow: super().__init__() 完成")
        self.window_detector = window_detector
        self.window_picker = window_picker
        self.current_window_info = None
        try:
            self.init_ui()
            logger.info("WindowDetectorWindow: init_ui() 完成")
        except Exception as e:
            logger.error(f"WindowDetectorWindow init_ui 失败: {e}", exc_info=True)
            raise
        
    def init_ui(self):
        self.setWindowTitle("窗口信息检测器")
        self.setFixedSize(650, 550)
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(10)
        
        btn_layout = QHBoxLayout()
        
        self.pick_btn = QPushButton("开始选择")
        self.pick_btn.setFixedHeight(32)
        self.pick_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.pick_btn.clicked.connect(self.start_pick)
        
        self.refresh_btn = QPushButton("刷新")
        self.refresh_btn.setFixedHeight(32)
        self.refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.refresh_btn.clicked.connect(self.refresh_info)
        
        self.copy_btn = QPushButton("复制信息")
        self.copy_btn.setFixedHeight(32)
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        self.copy_btn.clicked.connect(self.copy_info)
        
        self.save_btn = QPushButton("保存目标")
        self.save_btn.setFixedHeight(32)
        self.save_btn.setEnabled(False)
        self.save_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.save_btn.clicked.connect(self.save_target)
        
        self.close_btn = QPushButton("关闭")
        self.close_btn.setFixedHeight(32)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.close_btn.clicked.connect(self.close)
        
        btn_layout.addWidget(self.pick_btn)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.info_label = QLabel("窗口信息:")
        self.info_label.setStyleSheet("QLabel { font-weight: bold; font-size: 13px; color: #2c3e50; }")
        layout.addWidget(self.info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(130)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 12px;
            }
        """)
        layout.addWidget(self.info_text)
        
        self.edit_label = QLabel("输入框控件:")
        self.edit_label.setStyleSheet("QLabel { font-weight: bold; font-size: 13px; color: #2c3e50; }")
        layout.addWidget(self.edit_label)
        
        self.edit_tree = QTreeWidget()
        self.edit_tree.setHeaderLabels(["类型", "类名", "AutomationId", "名称"])
        self.edit_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        self.edit_tree.setMaximumHeight(120)
        layout.addWidget(self.edit_tree)
        
        self.tree_label = QLabel("完整控件树:")
        self.tree_label.setStyleSheet("QLabel { font-weight: bold; font-size: 13px; color: #2c3e50; }")
        layout.addWidget(self.tree_label)
        
        self.control_tree = QTreeWidget()
        self.control_tree.setHeaderLabels(["类型", "类名", "名称"])
        self.control_tree.setStyleSheet("""
            QTreeWidget {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                font-size: 11px;
            }
            QTreeWidget::item {
                padding: 2px;
            }
            QTreeWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.control_tree)
        
        self.status_label = QLabel("等待选择窗口...")
        self.status_label.setStyleSheet("QLabel { color: #7f8c8d; font-size: 11px; }")
        layout.addWidget(self.status_label)
    
    def start_pick(self):
        try:
            logger.info("开始选择窗口...")
            self.status_label.setText("请切换到目标窗口，等待1秒...")
            self.hide()
            
            QTimer.singleShot(1500, self._capture_foreground_window)
            
            logger.info("pick_window 已调用")
        except Exception as e:
            logger.error(f"start_pick 失败: {e}", exc_info=True)
            self.status_label.setText(f"选择失败: {e}")
            self.show()
    
    def _capture_foreground_window(self):
        try:
            logger.info("开始捕获前台窗口...")
            self.window_picker.pick_window(self.on_window_picked)
        except Exception as e:
            logger.error(f"捕获前台窗口失败: {e}", exc_info=True)
            self.show()
            self.status_label.setText(f"选择失败: {e}")
    
    def on_window_picked(self, window_data):
        try:
            hwnd = self._find_hwnd_by_title(window_data.get('title', ''), window_data.get('class_name', ''))
            if hwnd:
                self.current_window_info = self.window_detector.get_window_info(hwnd)
                self.display_window_info()
                self.load_control_tree()
                self.status_label.setText(f"已选择窗口: {self.current_window_info.get('title', '')[:30]}")
                self.save_btn.setEnabled(True)
            else:
                self.status_label.setText("未找到窗口句柄")
        except Exception as e:
            logger.error(f"选择窗口处理失败: {e}")
            self.status_label.setText(f"选择失败: {e}")
    
    def _find_hwnd_by_title(self, title, class_name):
        import ctypes
        from ctypes import wintypes
        
        hwnd = ctypes.windll.user32.FindWindowW(None, title)
        if hwnd:
            return hwnd
        
        def enum_windows_proc(hwnd, lParam):
            if hwnd:
                length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
                if length > 0:
                    buf = ctypes.create_unicode_buffer(length + 1)
                    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                    if title and title in buf.value:
                        lParam[0] = hwnd
            return True
        
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p))
        lParam = [0]
        ctypes.windll.user32.EnumWindows(EnumWindowsProc(enum_windows_proc), ctypes.cast(lParam, ctypes.c_void_p))
        return lParam[0]
    
    def display_window_info(self):
        if not self.current_window_info:
            return
        
        info = self.current_window_info
        text = f"""句柄(HWND): {info.get('hwnd', 0)}
窗口类名: {info.get('class_name', '')}
窗口标题: {info.get('title', '')}
进程ID: {info.get('process_id', 0)}
进程名: {info.get('process_name', '')}"""
        
        self.info_text.setPlainText(text)
    
    def load_control_tree(self):
        if not self.current_window_info:
            return
        
        hwnd = self.current_window_info.get('hwnd')
        if not hwnd:
            return
        
        self.edit_tree.clear()
        self.control_tree.clear()
        
        edit_controls = self.window_detector.get_edit_controls(hwnd)
        for edit in edit_controls:
            item = QTreeWidgetItem([
                edit.get('control_type', ''),
                edit.get('class_name', ''),
                edit.get('automation_id', ''),
                edit.get('name', '')
            ])
            self.edit_tree.addTopLevelItem(item)
        
        if edit_controls:
            self.edit_tree.expandAll()
        else:
            self.edit_tree.addTopLevelItem(QTreeWidgetItem(["未找到输入框", "", "", ""]))
        
        controls = self.window_detector.get_control_tree(hwnd)
        for ctrl in controls[:100]:
            item = QTreeWidgetItem([
                ctrl.get('control_type', ''),
                ctrl.get('class_name', ''),
                ctrl.get('name', '')
            ])
            item.setData(0, Qt.UserRole, ctrl.get('depth', 0))
            self.control_tree.addTopLevelItem(item)
        
        if controls:
            self.control_tree.expandToDepth(1)
    
    def refresh_info(self):
        if self.current_window_info:
            hwnd = self.current_window_info.get('hwnd')
            if hwnd:
                self.current_window_info = self.window_detector.get_window_info(hwnd)
                self.display_window_info()
                self.load_control_tree()
                self.status_label.setText("信息已刷新")
    
    def copy_info(self):
        if self.current_window_info:
            info = self.current_window_info
            text = f"类名: {info.get('class_name', '')}\n标题: {info.get('title', '')}\n进程: {info.get('process_name', '')}"
            clipboard = QClipboard()
            clipboard.setText(text)
            self.status_label.setText("已复制到剪贴板")
    
    def save_target(self):
        if not self.current_window_info:
            return
        
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        
        if 'target_windows' not in config:
            config['target_windows'] = []
        
        target = {
            'hwnd': self.current_window_info.get('hwnd', 0),
            'class_name': self.current_window_info.get('class_name', ''),
            'title': self.current_window_info.get('title', ''),
            'process_id': self.current_window_info.get('process_id', 0),
            'process_name': self.current_window_info.get('process_name', ''),
        }
        
        config['target_windows'].append(target)
        
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        self.status_label.setText("目标已保存")
        QMessageBox.information(self, "保存成功", "目标窗口配置已保存到 config.json")