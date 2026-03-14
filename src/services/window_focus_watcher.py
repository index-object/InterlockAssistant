import ctypes
import logging
from ctypes import wintypes
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class WindowFocusWatcher(QObject):
    window_focused = Signal(int, str, str)
    
    def __init__(self):
        super().__init__()
        self._hook = None
        self._target_class_names = []
        self._target_titles = []
        self._last_hwnd = 0
        self._instance = None
    
    def set_target_windows(self, class_names_or_titles):
        self._target_class_names = [name.strip().lower() for name in class_names_or_titles if name.strip()]
        self._target_titles = [name.strip().lower() for name in class_names_or_titles if name.strip()]
    
    def start(self):
        if self._hook is not None:
            return
        
        self._instance = self
        
        user32 = ctypes.windll.user32
        
        EVENT_SYSTEM_FOREGROUND = 3
        WINEVENT_OUTOFCONTEXT = 0
        
        WinEventProcType = ctypes.WINFUNCTYPE(
            None, 
            ctypes.c_void_p, 
            ctypes.c_uint, 
            ctypes.c_void_p, 
            ctypes.c_long, 
            ctypes.c_long, 
            ctypes.c_uint, 
            ctypes.c_uint
        )
        
        def win_event_proc(hook, event, hwnd, id_object, id_child, thread_id, timestamp):
            if event == 3 and hwnd and hwnd != self._instance._last_hwnd:
                self._instance._last_hwnd = hwnd
                try:
                    class_name = self._instance._get_window_class_name(hwnd)
                    title = self._instance._get_window_text(hwnd)
                    
                    if self._instance._is_target_window(class_name, title):
                        self._instance.window_focused.emit(hwnd, class_name, title)
                except Exception:
                    pass
        
        self._win_event_proc = WinEventProcType(win_event_proc)
        
        self._hook = user32.SetWinEventHook(
            EVENT_SYSTEM_FOREGROUND,
            EVENT_SYSTEM_FOREGROUND,
            None,
            self._win_event_proc,
            0,
            0,
            WINEVENT_OUTOFCONTEXT
        )
    
    def _get_window_class_name(self, hwnd):
        try:
            buffer = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(hwnd, buffer, 256)
            return buffer.value
        except Exception:
            return ""
    
    def _get_window_text(self, hwnd):
        try:
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return ""
            buffer = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
            return buffer.value
        except Exception:
            return ""
    
    def _is_target_window(self, class_name, title=""):
        if not self._target_class_names:
            return True
        class_lower = class_name.lower()
        title_lower = title.lower() if title else ""
        
        for target in self._target_class_names:
            if target in class_lower or target in title_lower:
                return True
        return False
    
    def stop(self):
        if self._hook:
            try:
                ctypes.windll.user32.UnhookWinEvent(self._hook)
            except Exception:
                pass
            self._hook = None
    
    def get_foreground_window_info(self):
        try:
            hwnd = ctypes.windll.user32.GetForegroundWindow()
            class_name = self._get_window_class_name(hwnd)
            text = self._get_window_text(hwnd)
            return {'hwnd': hwnd, 'class_name': class_name, 'text': text}
        except Exception:
            return {'hwnd': 0, 'class_name': '', 'text': ''}