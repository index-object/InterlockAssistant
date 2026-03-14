from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                                 QPushButton, QFrame, QGridLayout, QSizePolicy, QApplication)
from PySide6.QtCore import Qt, QPoint, QTimer
from PySide6.QtGui import QMouseEvent, QCursor, QIcon
from typing import Dict, Optional
import os
import json
from ..services.engineering_code import convert_to_engineering_code
from ..utils.icon_utils import get_icon_path, get_base_path


class FloatingWindow(QWidget):
    def __init__(self, window_info, database_service):
        super().__init__()
        icon_path = get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.window_info = window_info
        self.database_service = database_service
        self._drag_position = QPoint()
        self.access_name_map = self._load_config().get('access_name_mapping', {})
        self.init_ui()
        self.connect_signals()
    
    def _load_config(self) -> Dict:
        config_file = os.path.join(get_base_path(), 'config', 'config.json')
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    
    def init_ui(self):
        self.setWindowTitle("窗口数据监控")
        self.setMinimumSize(260, 420)
        self.resize(280, 500)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet("""
            FloatingWindow {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
                border-radius: 8px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        title_layout = QHBoxLayout()
        self.title_label = QLabel("等待数据...")
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #1E293B;
            }
        """)
        self.title_label.setCursor(Qt.OpenHandCursor)
        
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(24, 24)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: #EF4444;
                color: white;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #DC2626;
            }
        """)
        
        title_layout.addWidget(self.title_label, 1)
        title_layout.addWidget(self.close_btn)
        
        self.content_label = QLabel("监控数据:")
        self.content_label.setStyleSheet("QLabel { color: #64748B; font-size: 12px; }")
        
        self.content_display = QLabel("等待监控...")
        self.content_display.setWordWrap(True)
        self.content_display.setStyleSheet("""
            QLabel {
                background-color: #E2E8F0;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
                padding: 8px;
                font-size: 16px;
                color: #1E293B;
            }
        """)
        self.content_display.setMinimumHeight(36)
        self.content_display.setMaximumHeight(50)
        
        self.result_container = QWidget()
        self.result_layout = QVBoxLayout(self.result_container)
        self.result_layout.setContentsMargins(0, 0, 0, 0)
        self.result_layout.setSpacing(4)
        
        self.search_label = QLabel("检索结果:")
        self.search_label.setStyleSheet("QLabel { color: #64748B; font-size: 12px; }")
        
        self.result_card = QFrame()
        self.result_card.setStyleSheet("""
            QFrame {
                background-color: #FFFFFF;
                border: 1px solid #CBD5E1;
                border-radius: 6px;
            }
        """)
        self.result_card_layout = QVBoxLayout(self.result_card)
        self.result_card_layout.setContentsMargins(8, 8, 8, 8)
        self.result_card_layout.setSpacing(4)
        
        self.tag_container = QWidget()
        self.tag_container.setStyleSheet("QWidget { background: transparent; }")
        tag_layout = QHBoxLayout(self.tag_container)
        tag_layout.setContentsMargins(0, 0, 0, 0)
        tag_layout.setSpacing(8)
        
        self.tag_label = QLabel("--")
        self.tag_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2563EB;
            }
        """)
        
        self.tag_copy_btn = QPushButton("复制")
        self.tag_copy_btn.setFixedSize(40, 22)
        self.tag_copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-size: 10px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        self.tag_copy_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.tag_copy_btn.hide()
        
        tag_layout.addWidget(self.tag_label, 1)
        tag_layout.addWidget(self.tag_copy_btn)
        
        self.info_label = QLabel("")
        self.info_label.setStyleSheet("QLabel { font-size: 12px; color: #64748B; }")
        self.info_label.setWordWrap(True)
        
        self.range_label = QLabel("量程: -- ~ -- --")
        self.range_label.setStyleSheet("QLabel { font-size: 16px; color: #1E293B; font-weight: 500; }")
        
        self.alarm_title = QLabel("报警设置:")
        self.alarm_title.setStyleSheet("QLabel { font-size: 14px; color: #64748B; margin-top: 4px; }")
        
        self.alarm_grid = QWidget()
        self.alarm_grid_layout = QGridLayout(self.alarm_grid)
        self.alarm_grid_layout.setContentsMargins(0, 4, 0, 0)
        self.alarm_grid_layout.setSpacing(4)
        
        self.hihi_label = self._create_alarm_label("高高报")
        self.hi_label = self._create_alarm_label("高报")
        self.lo_label = self._create_alarm_label("低报")
        self.lolo_label = self._create_alarm_label("低低报")
        
        self.hihi_value = self._create_alarm_value_label()
        self.hi_value = self._create_alarm_value_label()
        self.lo_value = self._create_alarm_value_label()
        self.lolo_value = self._create_alarm_value_label()
        
        self.hihi_code_widget = self._create_engineering_code_widget()
        self.hi_code_widget = self._create_engineering_code_widget()
        self.lo_code_widget = self._create_engineering_code_widget()
        self.lolo_code_widget = self._create_engineering_code_widget()
        
        self.alarm_grid_layout.addWidget(self.hihi_label, 0, 0)
        self.alarm_grid_layout.addWidget(self.hi_label, 0, 1)
        self.alarm_grid_layout.addWidget(self.hihi_value, 1, 0)
        self.alarm_grid_layout.addWidget(self.hi_value, 1, 1)
        self.alarm_grid_layout.addWidget(self.hihi_code_widget, 2, 0)
        self.alarm_grid_layout.addWidget(self.hi_code_widget, 2, 1)
        self.alarm_grid_layout.addWidget(self.lo_label, 3, 0)
        self.alarm_grid_layout.addWidget(self.lolo_label, 3, 1)
        self.alarm_grid_layout.addWidget(self.lo_value, 4, 0)
        self.alarm_grid_layout.addWidget(self.lolo_value, 4, 1)
        self.alarm_grid_layout.addWidget(self.lo_code_widget, 5, 0)
        self.alarm_grid_layout.addWidget(self.lolo_code_widget, 5, 1)
        
        self.access_label = QLabel("访问名: --")
        self.access_label.setStyleSheet("QLabel { font-size: 12px; color: #94A3B8; margin-top: 4px; }")
        
        self.result_card_layout.addWidget(self.tag_container)
        self.result_card_layout.addWidget(self.info_label)
        self.result_card_layout.addWidget(self.range_label)
        self.result_card_layout.addWidget(self.alarm_title)
        self.result_card_layout.addWidget(self.alarm_grid)
        self.result_card_layout.addWidget(self.access_label)
        
        self.no_result_label = QLabel("无匹配结果")
        self.no_result_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #94A3B8;
                padding: 20px;
                background-color: #E2E8F0;
                border-radius: 6px;
            }
        """)
        self.no_result_label.setAlignment(Qt.AlignCenter)
        self.no_result_label.hide()
        
        layout.addLayout(title_layout)
        layout.addWidget(self.content_label)
        layout.addWidget(self.content_display)
        layout.addWidget(self.search_label)
        layout.addWidget(self.result_card)
        layout.addWidget(self.no_result_label)
    
    def _create_alarm_label(self, text: str) -> QLabel:
        label = QLabel(text)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                background-color: #E2E8F0;
                color: #64748B;
                font-size: 12px;
                padding: 4px;
                border-radius: 4px;
            }
        """)
        label.setMinimumHeight(22)
        return label
    
    def _create_alarm_value_label(self) -> QLabel:
        label = QLabel("--")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
            QLabel {
                background-color: #E2E8F0;
                color: #64748B;
                font-size: 14px;
                font-weight: 500;
                padding: 6px;
                border-radius: 4px;
            }
        """)
        label.setMinimumHeight(32)
        return label
    
    def _create_engineering_code_widget(self):
        container = QWidget()
        container.setStyleSheet("QWidget { background: transparent; }")
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)
        
        code_label = QLabel("工程码: --")
        code_label.setStyleSheet("""
            QLabel {
                background-color: #F1F5F9;
                color: #475569;
                font-size: 11px;
                padding: 4px;
                border-radius: 4px;
            }
        """)
        
        copy_btn = QPushButton("复制")
        copy_btn.setFixedSize(32, 18)
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-size: 9px;
                border-radius: 3px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
        copy_btn.setCursor(QCursor(Qt.PointingHandCursor))
        copy_btn.hide()
        
        layout.addWidget(code_label, 1)
        layout.addWidget(copy_btn)
        
        container.code_label = code_label
        container.copy_btn = copy_btn
        
        return container
    
    def _update_engineering_code_display(self, widget: QWidget, code: Optional[int]):
        if code is not None:
            widget.code_label.setText(f"工程码: {code}")
            widget.copy_btn.show()
            try:
                widget.copy_btn.clicked.disconnect()
            except RuntimeError:
                pass
            widget.copy_btn.clicked.connect(lambda checked=False, c=code, btn=widget.copy_btn: self._copy_to_clipboard(str(c), btn))
        else:
            widget.code_label.setText("工程码: --")
            widget.copy_btn.hide()
    
    def _copy_to_clipboard(self, text: str, btn: QPushButton):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        btn.setText("已复制")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #22C55E;
                color: white;
                font-size: 9px;
                border-radius: 3px;
                border: none;
            }
        """)
        QTimer.singleShot(1500, lambda: self._reset_copy_button(btn))
    
    def _reset_copy_button(self, btn: QPushButton):
        btn.setText("复制")
        btn.setStyleSheet("""
            QPushButton {
                background-color: #3B82F6;
                color: white;
                font-size: 9px;
                border-radius: 3px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2563EB;
            }
            QPushButton:pressed {
                background-color: #1D4ED8;
            }
        """)
    
    def _style_alarm_active(self, label: QLabel, value_label: QLabel, is_high: bool):
        if is_high:
            label.setStyleSheet("""
                QLabel {
                    background-color: #DC2626;
                    color: white;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 4px;
                    border-radius: 4px;
                }
            """)
            value_label.setStyleSheet("""
                QLabel {
                    background-color: #DC2626;
                    color: white;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
            """)
        else:
            label.setStyleSheet("""
                QLabel {
                    background-color: #F59E0B;
                    color: #1F2937;
                    font-size: 12px;
                    font-weight: bold;
                    padding: 4px;
                    border-radius: 4px;
                }
            """)
            value_label.setStyleSheet("""
                QLabel {
                    background-color: #F59E0B;
                    color: #1F2937;
                    font-size: 14px;
                    font-weight: bold;
                    padding: 6px;
                    border-radius: 4px;
                }
            """)
    
    def _style_alarm_inactive(self, label: QLabel, value_label: QLabel):
        label.setStyleSheet("""
            QLabel {
                background-color: #E2E8F0;
                color: #64748B;
                font-size: 12px;
                padding: 4px;
                border-radius: 4px;
            }
        """)
        value_label.setStyleSheet("""
            QLabel {
                background-color: #E2E8F0;
                color: #64748B;
                font-size: 14px;
                font-weight: 500;
                padding: 6px;
                border-radius: 4px;
            }
        """)
    
    def connect_signals(self):
        self.close_btn.clicked.connect(self.hide_to_tray)
    
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
    
    def update_content(self, text: str):
        self.content_display.setText(text[:80] + "..." if len(text) > 80 else text)
        
        core_id = self.database_service.extract_core_identifier(text)
        if core_id:
            matched = self.database_service.search_io_real_by_core_id(core_id, limit=10)
        else:
            matched = self.database_service.search_io_real(text, limit=10)
        
        if matched:
            self._display_result(matched[0])
        else:
            fuzzy_result = self.database_service.fuzzy_search_tag_name(text)
            if fuzzy_result:
                self._display_result(fuzzy_result, is_fuzzy=True)
            else:
                self._display_no_result()
    
    def _display_no_result(self):
        self.result_card.hide()
        self.no_result_label.show()
    
    def _display_result(self, real: Dict, is_fuzzy: bool = False):
        self.result_card.show()
        self.no_result_label.hide()
        
        tag_name = real.get('tag_name', '')
        comment = real.get('comment', '')
        eng_units = real.get('eng_units', '')
        min_eu = real.get('min_eu', '')
        max_eu = real.get('max_eu', '')
        item_name = real.get('item_name', '')
        access_name = real.get('access_name', '')
        
        prefix = "[模糊] " if is_fuzzy else ""
        self.tag_label.setText(f"{prefix}{tag_name}" if tag_name else "--")
        
        if tag_name:
            self.tag_copy_btn.show()
            try:
                self.tag_copy_btn.clicked.disconnect()
            except RuntimeError:
                pass
            self.tag_copy_btn.clicked.connect(lambda checked=False, t=tag_name: self._copy_to_clipboard(t, self.tag_copy_btn))
        else:
            self.tag_copy_btn.hide()
        
        info_parts = []
        device_name = self.access_name_map.get(access_name, '')
        if device_name:
            info_parts.append(f"装置: {device_name}")
        if comment:
            info_parts.append(f"注释: {comment}")
        self.info_label.setText("\n".join(info_parts) if info_parts else "")
        
        if min_eu != '' and max_eu != '':
            unit_str = f" {eng_units}" if eng_units else ""
            self.range_label.setText(f"量程: {min_eu} ~ {max_eu}{unit_str}")
        elif eng_units:
            self.range_label.setText(f"单位: {eng_units}")
        else:
            self.range_label.setText("量程: --")
        
        hihi_state = real.get('hihi_alarm_state')
        hi_state = real.get('hi_alarm_state')
        lo_state = real.get('lo_alarm_state')
        lolo_state = real.get('lolo_alarm_state')
        
        hihi_val = real.get('hihi_alarm_value')
        hi_val = real.get('hi_alarm_value')
        lo_val = real.get('lo_alarm_value')
        lolo_val = real.get('lolo_alarm_value')
        
        min_eu_val = min_eu if min_eu != '' else None
        max_eu_val = max_eu if max_eu != '' else None
        
        val_str = f" {eng_units}" if eng_units else ""
        
        if hihi_state is not None and hihi_state != 0 and hihi_val is not None:
            self.hihi_value.setText(f"{hihi_val}{val_str}")
            self._style_alarm_active(self.hihi_label, self.hihi_value, is_high=True)
            hihi_code = convert_to_engineering_code(hihi_val, min_eu_val, max_eu_val)
        else:
            self.hihi_value.setText("--")
            self._style_alarm_inactive(self.hihi_label, self.hihi_value)
            hihi_code = None
        
        if hi_state is not None and hi_state != 0 and hi_val is not None:
            self.hi_value.setText(f"{hi_val}{val_str}")
            self._style_alarm_active(self.hi_label, self.hi_value, is_high=True)
            hi_code = convert_to_engineering_code(hi_val, min_eu_val, max_eu_val)
        else:
            self.hi_value.setText("--")
            self._style_alarm_inactive(self.hi_label, self.hi_value)
            hi_code = None
        
        if lo_state is not None and lo_state != 0 and lo_val is not None:
            self.lo_value.setText(f"{lo_val}{val_str}")
            self._style_alarm_active(self.lo_label, self.lo_value, is_high=False)
            lo_code = convert_to_engineering_code(lo_val, min_eu_val, max_eu_val)
        else:
            self.lo_value.setText("--")
            self._style_alarm_inactive(self.lo_label, self.lo_value)
            lo_code = None
        
        if lolo_state is not None and lolo_state != 0 and lolo_val is not None:
            self.lolo_value.setText(f"{lolo_val}{val_str}")
            self._style_alarm_active(self.lolo_label, self.lolo_value, is_high=False)
            lolo_code = convert_to_engineering_code(lolo_val, min_eu_val, max_eu_val)
        else:
            self.lolo_value.setText("--")
            self._style_alarm_inactive(self.lolo_label, self.lolo_value)
            lolo_code = None
        
        self._update_engineering_code_display(self.hihi_code_widget, hihi_code)
        self._update_engineering_code_display(self.hi_code_widget, hi_code)
        self._update_engineering_code_display(self.lo_code_widget, lo_code)
        self._update_engineering_code_display(self.lolo_code_widget, lolo_code)
        
        self.access_label.setText(f"访问名: {item_name}" if item_name else "访问名: --")
    
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
            self.move(geometry.width() - self.width() - 20, 20)