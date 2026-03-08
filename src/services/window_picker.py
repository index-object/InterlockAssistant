import ctypes
import logging
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal, QTimer

logger = logging.getLogger(__name__)


class WindowPicker(QObject):
    window_picked = Signal(dict)
    
    def __init__(self):
        super().__init__()
        self._app = QApplication.instance()
        self._callback = None
        self._timer = None
    
    def pick_window(self, callback=None):
        try:
            logger.info("WindowPicker: pick_window 开始...")
            self._callback = callback
            
            self._get_foreground_window()
            
        except Exception as e:
            logger.error(f"WindowPicker: pick_window 失败: {e}", exc_info=True)
    
    def _get_foreground_window(self):
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            if hwnd:
                class_name = self._get_class(hwnd)
                title = self._get_title(hwnd)
                pid = self._get_process_id(hwnd)
                
                window_data = {
                    'hwnd': hwnd,
                    'class_name': class_name,
                    'title': title,
                    'process_id': pid,
                }
                logger.info(f"WindowPicker: 获取前台窗口: {window_data}")
                
                if self._callback:
                    self._callback(window_data)
                self.window_picked.emit(window_data)
        except Exception as e:
            logger.error(f"WindowPicker: 获取前台窗口失败: {e}", exc_info=True)
    
    def stop(self):
        if self._timer:
            self._timer.stop()
            self._timer = None
    
    def _get_class(self, hwnd):
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