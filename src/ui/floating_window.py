from PySide2.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QListWidget
from PySide2.QtCore import Qt
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
        self.setFixedSize(320, 220)
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
        
        self.title_label = QLabel("等待剪贴板...")
        self.title_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 13px;
                color: #2c3e50;
            }
        """)
        
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
        
        self.content_label = QLabel("剪贴板内容:")
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
    
    def hide_to_tray(self):
        self.hide()
    
    def copy_window_title(self):
        title = self.title_label.text()
        if title and title != "等待剪贴板...":
            clipboard = QClipboard()
            clipboard.setText(title)
    
    def update_content(self, text: str):
        self.content_edit.setPlainText(text[:100])
        results = self.database_service.search(text)
        self.result_list.clear()
        if not results:
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
        else:
            self.result_list.setStyleSheet("""
                QListWidget {
                    background-color: #ecf0f1;
                    border: 1px solid #bdc3c7;
                    border-radius: 4px;
                    font-size: 11px;
                }
            """)
            for result in results:
                self.result_list.addItem(f"{result['keyword']} → {result.get('description', '')}")
    
    def update_title(self, title: str):
        if title:
            self.title_label.setText(title)
        else:
            self.title_label.setText("未知窗口")
    
    def move_to_corner(self):
        from PySide2.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        if screen:
            geometry = screen.availableGeometry()
            self.move(geometry.width() - self.width() - 20, 
                     geometry.height() - self.height() - 60)