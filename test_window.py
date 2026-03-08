import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QLineEdit, QLabel, QTextEdit, QPushButton
from PySide6.QtCore import Qt


class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("测试窗口 - 用于测试自动捕获")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("输入框1:"))
        self.edit1 = QLineEdit()
        self.edit1.setPlaceholderText("请输入内容...")
        layout.addWidget(self.edit1)
        
        layout.addWidget(QLabel("输入框2:"))
        self.edit2 = QLineEdit()
        self.edit2.setPlaceholderText("请输入内容...")
        layout.addWidget(self.edit2)
        
        layout.addWidget(QLabel("多行文本框:"))
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("请输入多行内容...")
        layout.addWidget(self.text_edit)
        
        self.status_label = QLabel("窗口类名: TestWindow")
        self.status_label.setStyleSheet("color: gray; padding: 10px;")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        self.set_class_name()
    
    def set_class_name(self):
        hwnd = int(self.winId())
        try:
            import ctypes
            ctypes.windll.user32.SetWindowTextW(hwnd, "测试窗口")
        except:
            pass


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec())