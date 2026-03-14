from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from ..utils.icon_utils import get_icon_path


class TestInputDialog(QDialog):
    value_submitted = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        icon_path = get_icon_path()
        if icon_path:
            self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle("测试模式 - 输入测试值")
        self.setFixedSize(400, 150)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        label = QLabel("请输入测试值（模拟窗口读取的数据）:")
        layout.addWidget(label)
        
        self.input_edit = QLineEdit()
        self.input_edit.setPlaceholderText("例如: AI_001 或 123.45")
        self.input_edit.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                font-size: 14px;
                border: 2px solid #3498db;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.input_edit)
        
        btn_layout = QHBoxLayout()
        
        self.submit_btn = QPushButton("提交测试")
        self.submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.submit_btn.clicked.connect(self.on_submit)
        
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 8px 20px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.cancel_btn.clicked.connect(self.close)
        
        btn_layout.addStretch()
        btn_layout.addWidget(self.submit_btn)
        btn_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(btn_layout)
    
    def on_submit(self):
        value = self.input_edit.text().strip()
        if value:
            self.value_submitted.emit(value)
            self.input_edit.clear()
            self.input_edit.setFocus()
