from PySide2.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, 
                                  QListWidgetItem, QPushButton, QLineEdit, QGroupBox, QMessageBox)
from PySide2.QtCore import Qt
import json

from src.services.window_info import WindowInfo


class ConfigWindow(QDialog):
    def __init__(self, database_service, hotkey_manager, parent=None):
        super().__init__(parent)
        self.database_service = database_service
        self.hotkey_manager = hotkey_manager
        self.window_info = WindowInfo()
        self.init_ui()
        self.load_data()
    
    def init_ui(self):
        self.setWindowTitle("配置")
        self.setMinimumSize(450, 400)
        
        layout = QVBoxLayout()
        
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QVBoxLayout()
        hotkey_layout.addWidget(QLabel("显示/隐藏:"))
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("例如: Ctrl+Shift+V")
        hotkey_layout.addWidget(self.hotkey_edit)
        hotkey_group.setLayout(hotkey_layout)
        
        filter_group = QGroupBox("窗口过滤")
        filter_layout = QVBoxLayout()
        self.filter_list = QListWidget()
        self.filter_list.setSelectionMode(QListWidget.MultiSelection)
        filter_layout.addWidget(self.filter_list)
        filter_btn_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("刷新窗口")
        self.clear_filter_btn = QPushButton("清除")
        filter_btn_layout.addWidget(self.refresh_btn)
        filter_btn_layout.addWidget(self.clear_filter_btn)
        filter_layout.addLayout(filter_btn_layout)
        filter_group.setLayout(filter_layout)
        
        keyword_group = QGroupBox("关键词管理")
        keyword_layout = QVBoxLayout()
        self.keyword_list = QListWidget()
        keyword_input_layout = QHBoxLayout()
        self.keyword_edit = QLineEdit()
        self.keyword_edit.setPlaceholderText("输入关键词")
        self.keyword_desc_edit = QLineEdit()
        self.keyword_desc_edit.setPlaceholderText("描述(可选)")
        self.add_keyword_btn = QPushButton("添加")
        keyword_input_layout.addWidget(self.keyword_edit)
        keyword_input_layout.addWidget(self.keyword_desc_edit)
        keyword_input_layout.addWidget(self.add_keyword_btn)
        keyword_layout.addWidget(self.keyword_list)
        keyword_layout.addLayout(keyword_input_layout)
        keyword_group.setLayout(keyword_layout)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(hotkey_group)
        layout.addWidget(filter_group)
        layout.addWidget(keyword_group)
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        self.save_btn.clicked.connect(self.save_config)
        self.cancel_btn.clicked.connect(self.reject)
        self.refresh_btn.clicked.connect(self.load_window_filters)
        self.clear_filter_btn.clicked.connect(self.clear_filters)
        self.add_keyword_btn.clicked.connect(self.add_keyword)
    
    def load_data(self):
        self.hotkey_edit.setText(self.hotkey_manager.get_hotkey('show_hide'))
        
        keywords = self.database_service.get_all_keywords()
        self.keyword_list.clear()
        for kw in keywords:
            self.keyword_list.addItem(f"{kw['id']}: {kw['keyword']} - {kw.get('description', '')}")
        
        self.load_window_filters()
    
    def load_window_filters(self):
        self.filter_list.clear()
        windows = self.window_info.get_all_windows()
        
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                saved_filters = config.get('window_filters', [])
        except:
            saved_filters = []
        
        for win_info in windows:
            if isinstance(win_info, dict):
                title = win_info.get('title', '')
                class_name = win_info.get('class_name', '')
                display_text = f"{title} (类名: {class_name})" if class_name else title
            else:
                display_text = win_info
                class_name = ""
            
            if display_text:
                item = QListWidgetItem(display_text)
                item.setData(Qt.UserRole, display_text)
                
                for sf in saved_filters:
                    if sf in display_text or (isinstance(win_info, dict) and sf in class_name):
                        item.setCheckState(Qt.Checked)
                        break
                else:
                    item.setCheckState(Qt.Unchecked)
                
                self.filter_list.addItem(item)
    
    def clear_filters(self):
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            item.setCheckState(Qt.Unchecked)
    
    def add_keyword(self):
        keyword = self.keyword_edit.text().strip()
        if not keyword:
            QMessageBox.warning(self, "警告", "请输入关键词")
            return
        
        description = self.keyword_desc_edit.text().strip()
        self.database_service.add_keyword(keyword, description)
        
        self.keyword_edit.clear()
        self.keyword_desc_edit.clear()
        
        keywords = self.database_service.get_all_keywords()
        self.keyword_list.clear()
        for kw in keywords:
            self.keyword_list.addItem(f"{kw['id']}: {kw['keyword']} - {kw.get('description', '')}")
    
    def save_config(self):
        hotkey = self.hotkey_edit.text().strip()
        if hotkey:
            self.hotkey_manager.set_hotkey('show_hide', hotkey)
        
        filters = []
        for i in range(self.filter_list.count()):
            item = self.filter_list.item(i)
            if item.checkState() == Qt.Checked:
                display_text = item.data(Qt.UserRole)
                if display_text:
                    if "(类名:" in display_text:
                        class_name = display_text.split("(类名:")[1].rstrip(")")
                        filters.append(class_name)
                    else:
                        filters.append(display_text)
        
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
        except:
            config = {}
        config['window_filters'] = filters
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
        
        self.accept()