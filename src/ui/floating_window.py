from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QListWidget
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QClipboard, QMouseEvent
from typing import Dict
import os

class FloatingWindow(QWidget):
    def __init__(self, window_info, database_service):
        super().__init__()
        self.window_info = window_info
        self.database_service = database_service
        self._drag_position = QPoint()
        self.access_name_map = self._load_access_name_map()
        self.init_ui()
        self.connect_signals()
    
    def _load_access_name_map(self) -> Dict[str, str]:
        mapping = {}
        map_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                                'config', 'access_name映射.txt')
        try:
            with open(map_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if '→' in line:
                        parts = line.split('→')
                        if len(parts) == 2:
                            key = parts[0].strip()
                            value = parts[1].strip()
                            mapping[key] = value
        except Exception:
            pass
        return mapping
    
    def init_ui(self):
        self.setWindowTitle("窗口数据监控")
        self.setMinimumSize(400, 350)
        self.resize(400, 450)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            FloatingWindow {
                background-color: #ffffff;
                border: 2px solid #3498db;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)
        layout.setSpacing(8)
        
        title_layout = QHBoxLayout()
        self.copy_btn = QPushButton("📋")
        self.copy_btn.setFixedSize(30, 28)
        self.copy_btn.setToolTip("复制窗口来源")
        self.copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        self.title_label = QLabel("等待数据...")
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
            }
        """)
        self.title_label.setCursor(Qt.OpenHandCursor)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 4px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        title_layout.addWidget(self.copy_btn)
        title_layout.addWidget(self.title_label, 1)
        title_layout.addWidget(self.close_btn)
        
        self.content_label = QLabel("监控数据:")
        self.content_label.setStyleSheet("QLabel { color: #7f8c8d; font-size: 12px; }")
        
        self.content_edit = QTextEdit()
        self.content_edit.setReadOnly(True)
        self.content_edit.setMaximumHeight(60)
        self.content_edit.setStyleSheet("""
            QTextEdit {
                background-color: #ecf0f1;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                padding: 4px;
                font-size: 11px;
            }
        """)
        
        self.search_label = QLabel("检索结果:")
        self.search_label.setStyleSheet("QLabel { color: #7f8c8d; font-size: 12px; }")
        
        self.result_list = QListWidget()
        self.result_list.setMinimumHeight(200)
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
        
        layout.addLayout(title_layout)
        layout.addWidget(self.content_label)
        layout.addWidget(self.content_edit)
        layout.addWidget(self.search_label)
        layout.addWidget(self.result_list)
    
    def connect_signals(self):
        self.close_btn.clicked.connect(self.hide_to_tray)
        self.copy_btn.clicked.connect(self.copy_window_title)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._drag_position = event.globalPosition().toPoint()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            delta = event.globalPosition().toPoint() - self._drag_position
            self.move(self.pos() + delta)
            self._drag_position = event.globalPosition().toPoint()
            event.accept()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.isMaximized():
                self.showNormal()
            else:
                self.showMaximized()
            event.accept()
    
    def hide_to_tray(self):
        self.hide()
    
    def copy_window_title(self):
        title = self.title_label.text()
        if title and title != "等待数据...":
            clipboard = QClipboard()
            clipboard.setText(title)
    
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
    
    def _get_alarm_info(self, real: Dict) -> str:
        parts = []
        alarm_labels = {
            'lolo': ('低低报', 'lolo_alarm_state', 'lolo_alarm_value'),
            'lo': ('低报', 'lo_alarm_state', 'lo_alarm_value'),
            'hi': ('高报', 'hi_alarm_state', 'hi_alarm_value'),
            'hihi': ('高高报', 'hihi_alarm_state', 'hihi_alarm_value'),
        }
        
        for key in ['hihi', 'hi', 'lo', 'lolo']:
            label, state_key, value_key = alarm_labels[key]
            state = real.get(state_key)
            if state is not None and state != 0:
                val = real.get(value_key)
                if val is not None:
                    parts.append(f"{label}: {val}")
        
        return " | ".join(parts) if parts else "无"
    
    def update_title(self, title: str):
        if title:
            self.title_label.setText(title)
        else:
            self.title_label.setText("监控中...")
    
    def move_to_corner(self):
        from PySide6.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()