import ctypes
from ctypes import wintypes

class WindowInfo:
    def __init__(self):
        self.user32 = ctypes.windll.user32
    
    def get_foreground_window(self):
        return self.user32.GetForegroundWindow()
    
    def get_window_text(self, hwnd=None):
        if hwnd is None:
            hwnd = self.get_foreground_window()
        length = self.user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return ""
        buffer = ctypes.create_unicode_buffer(length + 1)
        self.user32.GetWindowTextW(hwnd, buffer, length + 1)
        return buffer.value
    
    def get_window_class_name(self, hwnd=None):
        if hwnd is None:
            hwnd = self.get_foreground_window()
        buffer = ctypes.create_unicode_buffer(256)
        self.user32.GetClassNameW(hwnd, buffer, 256)
        return buffer.value
    
    def get_window_title(self):
        return self.get_window_text()
    
    def get_window_info(self):
        hwnd = self.get_foreground_window()
        return {
            'title': self.get_window_text(hwnd),
            'class_name': self.get_window_class_name(hwnd),
            'hwnd': hwnd
        }
    
    def should_monitor(self, filters: list) -> bool:
        if not filters:
            return True
        
        hwnd = self.get_foreground_window()
        title = self.get_window_text(hwnd)
        class_name = self.get_window_class_name(hwnd)
        
        title_lower = title.lower() if title else ""
        class_name_lower = class_name.lower() if class_name else ""
        
        for f in filters:
            if not f:
                continue
            f_stripped = f.strip()
            f_lower = f_stripped.lower()
            
            if f_lower in title_lower or f_lower in class_name_lower:
                return True
        
        return False
    
    def get_all_windows(self):
        windows = []
        
        EnumWindows = self.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = self.user32.GetWindowTextW
        GetWindowTextLength = self.user32.GetWindowTextLengthW
        IsWindowVisible = self.user32.IsWindowVisible
        GetClassName = self.user32.GetClassNameW
        
        def callback(hwnd, lParam):
            if hwnd and IsWindowVisible(hwnd):
                length = GetWindowTextLength(hwnd)
                if length > 0:
                    buffer = ctypes.create_unicode_buffer(length + 1)
                    GetWindowText(hwnd, buffer, length + 1)
                    title = buffer.value
                    
                    class_buffer = ctypes.create_unicode_buffer(256)
                    GetClassName(hwnd, class_buffer, 256)
                    class_name = class_buffer.value
                    
                    if title and title not in windows:
                        info = {
                            'title': title,
                            'class_name': class_name
                        }
                        windows.append(info)
            return True
        
        try:
            EnumWindows(EnumWindowsProc(callback), 0)
        except Exception:
            pass
        
        return windows