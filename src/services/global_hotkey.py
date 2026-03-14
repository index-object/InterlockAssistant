import ctypes
from ctypes import wintypes
from PySide6.QtCore import QObject, Signal
import logging

logger = logging.getLogger(__name__)

user32 = ctypes.windll.user32

WM_HOTKEY = 0x0312

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008
MOD_NOREPEAT = 0x4000

VK_MAP = {
    'A': 0x41, 'B': 0x42, 'C': 0x43, 'D': 0x44, 'E': 0x45,
    'F': 0x46, 'G': 0x47, 'H': 0x48, 'I': 0x49, 'J': 0x4A,
    'K': 0x4B, 'L': 0x4C, 'M': 0x4D, 'N': 0x4E, 'O': 0x4F,
    'P': 0x50, 'Q': 0x51, 'R': 0x52, 'S': 0x53, 'T': 0x54,
    'U': 0x55, 'V': 0x56, 'W': 0x57, 'X': 0x58, 'Y': 0x59,
    'Z': 0x5A,
    '0': 0x30, '1': 0x31, '2': 0x32, '3': 0x33, '4': 0x34,
    '5': 0x35, '6': 0x36, '7': 0x37, '8': 0x38, '9': 0x39,
    'F1': 0x70, 'F2': 0x71, 'F3': 0x72, 'F4': 0x73,
    'F5': 0x74, 'F6': 0x75, 'F7': 0x76, 'F8': 0x77,
    'F9': 0x78, 'F10': 0x79, 'F11': 0x7A, 'F12': 0x7B,
    'Space': 0x20, 'Enter': 0x0D, 'Tab': 0x09,
    'Escape': 0x1B, 'Esc': 0x1B,
    'Insert': 0x2D, 'Delete': 0x2E,
    'Home': 0x24, 'End': 0x23,
    'PageUp': 0x21, 'PageDown': 0x22,
    'Up': 0x26, 'Down': 0x28, 'Left': 0x25, 'Right': 0x27,
    'Plus': 0xBB, 'Minus': 0xBD,
}


class GlobalHotkeyManager(QObject):
    hotkey_pressed = Signal(int)
    
    _instance = None
    _initialized = False
    
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if GlobalHotkeyManager._initialized:
            return
        super().__init__()
        GlobalHotkeyManager._initialized = True
        
        self._hotkeys = {}
        self._next_id = 1
        self._hwnd = None
        self._original_wndproc = None
        logger.info("GlobalHotkeyManager 初始化完成")
    
    def register(self, hotkey_str: str, callback) -> int:
        modifiers, vk = self._parse_hotkey(hotkey_str)
        if vk is None:
            logger.error(f"无法解析热键: {hotkey_str}")
            return -1
        
        hotkey_id = self._next_id
        self._next_id += 1
        
        if not user32.RegisterHotKey(None, hotkey_id, modifiers, vk):
            error = ctypes.get_last_error()
            logger.error(f"注册热键失败: {hotkey_str}, 错误码: {error}")
            return -1
        
        self._hotkeys[hotkey_id] = {
            'hotkey_str': hotkey_str,
            'callback': callback,
            'modifiers': modifiers,
            'vk': vk
        }
        
        logger.info(f"成功注册全局热键: {hotkey_str} (ID: {hotkey_id})")
        return hotkey_id
    
    def unregister(self, hotkey_id: int) -> bool:
        if hotkey_id not in self._hotkeys:
            return False
        
        if user32.UnregisterHotKey(None, hotkey_id):
            del self._hotkeys[hotkey_id]
            logger.info(f"成功注销热键 (ID: {hotkey_id})")
            return True
        else:
            error = ctypes.get_last_error()
            logger.error(f"注销热键失败, 错误码: {error}")
            return False
    
    def unregister_all(self):
        for hotkey_id in list(self._hotkeys.keys()):
            self.unregister(hotkey_id)
    
    def handle_hotkey(self, hotkey_id: int):
        if hotkey_id in self._hotkeys:
            callback = self._hotkeys[hotkey_id]['callback']
            if callback:
                callback()
    
    def _parse_hotkey(self, hotkey_str: str) -> tuple:
        modifiers = 0
        parts = hotkey_str.replace(' ', '').split('+')
        
        vk = None
        for part in parts:
            part_lower = part.lower()
            if part_lower in ('ctrl', 'control'):
                modifiers |= MOD_CONTROL
            elif part_lower == 'alt':
                modifiers |= MOD_ALT
            elif part_lower == 'shift':
                modifiers |= MOD_SHIFT
            elif part_lower in ('win', 'meta', 'super'):
                modifiers |= MOD_WIN
            else:
                if part in VK_MAP:
                    vk = VK_MAP[part]
                elif part.upper() in VK_MAP:
                    vk = VK_MAP[part.upper()]
                elif len(part) == 1:
                    vk = ord(part.upper())
        
        modifiers |= MOD_NOREPEAT
        return modifiers, vk