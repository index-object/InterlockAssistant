import ctypes
from ctypes import wintypes
import threading
from PySide2.QtWidgets import QApplication


class WindowPicker:
    def __init__(self):
        self._app = QApplication.instance()
        self._hook = None
        self._callback = None
        self._thread = None
    
    def pick_window(self, callback):
        self._callback = callback
        
        def mouse_proc(n_code, w_param, l_param):
            if n_code == 0 and w_param == 0x0201:
                class POINT(ctypes.Structure):
                    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]
                
                pt = POINT.from_address(l_param)
                hwnd = ctypes.windll.user32.WindowFromPoint(pt)
                if hwnd:
                    hwnd = ctypes.windll.user32.GetAncestor(hwnd, 2)
                    class_name = self._get_class(hwnd)
                    title = self._get_title(hwnd)
                    if self._callback:
                        self._callback({'class_name': class_name, 'title': title})
                
                ctypes.windll.user32.UnhookWindowsHookEx(self._hook)
                return 1
            
            return ctypes.windll.user32.CallNextHookEx(self._hook, n_code, w_param, l_param)
        
        WH_MOUSE_LL = 14
        HOOKPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_void_p)
        
        self._hook = ctypes.windll.user32.SetWindowsHookExW(WH_MOUSE_LL, HOOKPROC(mouse_proc), None, 0)
        
        def run_loop():
            msg = wintypes.MSG()
            while self._hook:
                ret = ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if ret == 0:
                    break
        
        self._thread = threading.Thread(target=run_loop, daemon=True)
        self._thread.start()
    
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