import win32clipboard
import threading
import time
from PySide6.QtCore import QObject, Signal, QTimer

class ClipboardWatcher(QObject):
    clipboard_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self.last_content = ""
        self._running = False
        self._timer = None
    
    def start(self):
        self._running = True
        self._timer = QTimer()
        self._timer.timeout.connect(self._check_clipboard)
        self._timer.start(300)
    
    def stop(self):
        self._running = False
        if self._timer:
            self._timer.stop()
    
    def _check_clipboard(self):
        try:
            current = self._get_text()
            if current and current != self.last_content:
                self.last_content = current
                self.clipboard_changed.emit(current)
        except Exception:
            pass
    
    def _get_text(self):
        try:
            win32clipboard.OpenClipboard(None)
            try:
                if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                    text = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT)
                    if text:
                        return text.decode('gbk', errors='ignore')
            finally:
                win32clipboard.CloseClipboard()
        except Exception:
            pass
        return ""
    
    def get_current_content(self):
        return self._get_text()