import ctypes
import logging
from ctypes import wintypes

logger = logging.getLogger(__name__)


class UIAutomationReader:
    def __init__(self):
        pass
    
    def read_window_text(self, hwnd):
        logger.info(f"开始读取窗口文本: hwnd={hwnd}")
        
        title = self._get_window_title(hwnd)
        class_name = self._get_window_class_name(hwnd)
        logger.info(f"窗口: hwnd={hwnd}, class={class_name}, title={title}")
        
        all_texts = []
        
        child = ctypes.windll.user32.GetWindow(hwnd, 5)
        while child and child != 0:
            try:
                child_class = self._get_window_class_name(child)
                child_title = self._get_window_text(child)
                
                logger.info(f"子控件: hwnd={child}, class={child_class}, title={child_title}")
                
                text = self._try_read_qt_edit(child, child_class)
                if text:
                    all_texts.append(text)
                    logger.info(f"读取到文本: {text}")
                    
            except Exception as e:
                logger.error(f"处理子控件失败: {e}")
            
            child = ctypes.windll.user32.GetWindow(child, 2)
        
        result = '\n'.join(all_texts)
        logger.info(f"最终结果: {result[:50] if result else '空'}")
        return result
    
    def _get_window_title(self, hwnd):
        try:
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length == 0:
                return ""
            buffer = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buffer, length + 1)
            return buffer.value
        except:
            return ""
    
    def _get_window_class_name(self, hwnd):
        try:
            buffer = ctypes.create_unicode_buffer(256)
            ctypes.windll.user32.GetClassNameW(hwnd, buffer, 256)
            return buffer.value
        except:
            return ""
    
    def _get_window_text(self, hwnd):
        return self._get_window_title(hwnd)
    
    def _try_read_qt_edit(self, hwnd, class_name):
        class_lower = class_name.lower() if class_name else ""
        
        if 'lineedit' in class_lower or 'qlineedit' in class_lower:
            try:
                buf_len = ctypes.windll.user32.SendMessageW(hwnd, 0x000E, 0, 0)
                if buf_len > 0:
                    buf = ctypes.create_unicode_buffer(buf_len + 1)
                    ctypes.windll.user32.SendMessageW(hwnd, 0x000D, buf_len + 1, buf)
                    return buf.value
            except Exception as e:
                logger.error(f"读取 QLineEdit 失败: {e}")
        
        if 'textedit' in class_lower or 'qtextedit' in class_lower:
            try:
                buf_len = ctypes.windll.user32.SendMessageW(hwnd, 0x000E, 0, 0)
                if buf_len > 0:
                    buf = ctypes.create_unicode_buffer(buf_len + 1)
                    ctypes.windll.user32.SendMessageW(hwnd, 0x000D, buf_len + 1, buf)
                    return buf.value
            except Exception as e:
                logger.error(f"读取 QTextEdit 失败: {e}")
        
        if 'edit' in class_lower or 'richedit' in class_lower:
            try:
                buf_len = ctypes.windll.user32.SendMessageW(hwnd, 0x000E, 0, 0)
                if buf_len > 0:
                    buf = ctypes.create_unicode_buffer(buf_len + 1)
                    ctypes.windll.user32.SendMessageW(hwnd, 0x000D, buf_len + 1, buf)
                    return buf.value
            except Exception as e:
                logger.error(f"读取 Edit 失败: {e}")
        
        return ""
    
    def find_edit_controls(self, hwnd):
        return []