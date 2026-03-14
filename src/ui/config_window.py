from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                                   QPushButton, QLineEdit, QGroupBox, QSpinBox, QMessageBox)
import json
import os


class ConfigWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'config', 'config.json'
        )
        self.config = self._load_config()
        self.init_ui()
        self.load_data()
    
    def _load_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "hotkey": {"show_hide": "Ctrl+Shift+V"},
                "engineering_code": {"min_code": 819, "max_code": 4095},
                "target_window": {
                    "title": "Item Properties",
                    "process_name": "TS1131.exe",
                    "target_control": {"name_pattern": "^\\s*Set Value:\\s*(.+)$"}
                }
            }
    
    def init_ui(self):
        self.setWindowTitle("配置")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        hotkey_group = QGroupBox("快捷键设置")
        hotkey_layout = QVBoxLayout()
        hotkey_layout.addWidget(QLabel("显示/隐藏:"))
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("例如: Ctrl+Shift+V")
        hotkey_layout.addWidget(self.hotkey_edit)
        hotkey_group.setLayout(hotkey_layout)
        
        code_group = QGroupBox("工程量代码设置")
        code_layout = QVBoxLayout()
        
        min_layout = QHBoxLayout()
        min_layout.addWidget(QLabel("最小代码值:"))
        self.min_code_spin = QSpinBox()
        self.min_code_spin.setRange(0, 65535)
        min_layout.addWidget(self.min_code_spin)
        min_layout.addStretch()
        code_layout.addLayout(min_layout)
        
        max_layout = QHBoxLayout()
        max_layout.addWidget(QLabel("最大代码值:"))
        self.max_code_spin = QSpinBox()
        self.max_code_spin.setRange(0, 65535)
        max_layout.addWidget(self.max_code_spin)
        max_layout.addStretch()
        code_layout.addLayout(max_layout)
        
        code_group.setLayout(code_layout)
        
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("保存")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addStretch()
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addWidget(hotkey_group)
        layout.addWidget(code_group)
        layout.addStretch()
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        self.save_btn.clicked.connect(self.save_config)
        self.cancel_btn.clicked.connect(self.reject)
    
    def load_data(self):
        hotkey = self.config.get('hotkey', {})
        self.hotkey_edit.setText(hotkey.get('show_hide', 'Ctrl+Shift+V'))
        
        eng_code = self.config.get('engineering_code', {})
        self.min_code_spin.setValue(eng_code.get('min_code', 819))
        self.max_code_spin.setValue(eng_code.get('max_code', 4095))
    
    def save_config(self):
        self.config['hotkey']['show_hide'] = self.hotkey_edit.text().strip()
        self.config['engineering_code']['min_code'] = self.min_code_spin.value()
        self.config['engineering_code']['max_code'] = self.max_code_spin.value()
        
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            QMessageBox.information(self, "成功", "配置已保存")
            self.accept()
        except Exception as e:
            QMessageBox.warning(self, "错误", f"保存配置失败: {e}")