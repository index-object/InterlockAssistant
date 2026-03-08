import logging
import ctypes
from ctypes import wintypes
from PySide6.QtCore import QObject, Signal

logger = logging.getLogger(__name__)


class WindowDetector(QObject):
    window_selected = Signal(dict)
    controls_updated = Signal(list)
    
    def __init__(self):
        super().__init__()
        self._target_hwnd = None
        self._control_tree = []
    
    def get_window_info(self, hwnd):
        info = {
            'hwnd': hwnd,
            'class_name': self._get_class_name(hwnd),
            'title': self._get_title(hwnd),
            'process_name': self._get_process_name(hwnd),
            'process_id': self._get_process_id(hwnd),
        }
        self._target_hwnd = hwnd
        logger.info(f"获取窗口信息: {info}")
        return info
    
    def get_control_tree(self, hwnd):
        try:
            import uiautomation as auto
            root = auto.WindowControl(searchDepth=1, handle=hwnd)
            if root.Exists(0.5):
                self._control_tree = self._build_control_tree(root, max_depth=20)
                logger.info(f"获取到 {len(self._control_tree)} 个控件")
                return self._control_tree
            else:
                root = auto.Control(handle=hwnd)
                if root:
                    self._control_tree = self._build_control_tree(root, max_depth=20)
                    logger.info(f"获取到 {len(self._control_tree)} 个控件")
                    return self._control_tree
        except Exception as e:
            logger.error(f"获取控件树失败: {e}", exc_info=True)
        return []
    
    def _build_control_tree(self, control, depth=0, max_depth=10):
        if depth > max_depth:
            return []
        
        controls = []
        try:
            control_type = control.ControlTypeName if hasattr(control, 'ControlTypeName') else ''
            class_name = control.ClassName if hasattr(control, 'ClassName') and control.ClassName else ''
            name = control.Name if hasattr(control, 'Name') and control.Name else ''
            
            if control_type or class_name or name:
                try:
                    rect = control.BoundingRectangle
                    rect_info = {
                        'left': int(rect.left),
                        'top': int(rect.top),
                        'right': int(rect.right),
                        'bottom': int(rect.bottom)
                    }
                except:
                    rect_info = {}
                
                try:
                    is_enabled = control.IsEnabled if hasattr(control, 'IsEnabled') else None
                except:
                    is_enabled = None
                
                try:
                    is_visible = control.IsVisible if hasattr(control, 'IsVisible') else None
                except:
                    is_visible = None
                
                try:
                    value = control.Value if hasattr(control, 'Value') and control.Value else ''
                except:
                    value = ''
                
                controls.append({
                    'depth': depth,
                    'control_type': control_type,
                    'class_name': class_name,
                    'name': name[:200] if name else '',
                    'automation_id': control.AutomationId if hasattr(control, 'AutomationId') and control.AutomationId else '',
                    'rect': rect_info,
                    'is_enabled': is_enabled,
                    'is_visible': is_visible,
                    'value': str(value)[:200] if value else '',
                })
            
            children = control.GetChildren()
            for child in children:
                controls.extend(self._build_control_tree(child, depth + 1, max_depth))
        except Exception as e:
            logger.debug(f"遍历控件时出错: {e}")
        
        return controls
    
    def get_edit_controls(self, hwnd=None):
        hwnd = hwnd or self._target_hwnd
        if not hwnd:
            return []
        
        edit_controls = []
        try:
            import uiautomation as auto
            root = auto.WindowControl(searchDepth=1, handle=hwnd)
            if not root.Exists(0.5):
                root = auto.Control(handle=hwnd)
            if root:
                edit_controls = self._find_edit_controls(root, max_depth=20)
                logger.info(f"找到 {len(edit_controls)} 个输入框控件")
        except Exception as e:
            logger.error(f"获取输入框控件失败: {e}", exc_info=True)
        
        return edit_controls
    
    def _find_edit_controls(self, control, depth=0, max_depth=15):
        if depth > max_depth:
            return []
        
        edit_controls = []
        try:
            control_type = control.ControlTypeName if hasattr(control, 'ControlTypeName') else ''
            
            if 'Edit' in control_type or 'Document' in control_type:
                class_name = control.ClassName if hasattr(control, 'ClassName') and control.ClassName else ''
                name = control.Name if hasattr(control, 'Name') and control.Name else ''
                automation_id = control.AutomationId if hasattr(control, 'AutomationId') and control.AutomationId else ''
                
                try:
                    rect = control.BoundingRectangle
                    rect_info = {
                        'left': int(rect.left),
                        'top': int(rect.top),
                        'right': int(rect.right),
                        'bottom': int(rect.bottom)
                    }
                except:
                    rect_info = {}
                
                try:
                    is_enabled = control.IsEnabled if hasattr(control, 'IsEnabled') else None
                except:
                    is_enabled = None
                
                try:
                    value = control.Value if hasattr(control, 'Value') else ''
                except:
                    value = ''
                
                try:
                    is_readonly = control.IsReadOnly if hasattr(control, 'IsReadOnly') else None
                except:
                    is_readonly = None
                
                edit_controls.append({
                    'control_type': control_type,
                    'class_name': class_name,
                    'name': name[:200] if name else '',
                    'automation_id': automation_id,
                    'rect': rect_info,
                    'is_enabled': is_enabled,
                    'is_readonly': is_readonly,
                    'value': str(value)[:200] if value else '',
                })
            
            children = control.GetChildren()
            for child in children:
                edit_controls.extend(self._find_edit_controls(child, depth + 1, max_depth))
        except Exception:
            pass
        
        return edit_controls
    
    def _get_class_name(self, hwnd):
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
    
    def _get_process_name(self, hwnd):
        try:
            pid = self._get_process_id(hwnd)
            if pid:
                handle = ctypes.windll.kernel32.OpenProcess(0x400, False, pid)
                if handle:
                    ctypes.windll.kernel32.CloseHandle(handle)
                    import psutil
                    return psutil.Process(pid).name()
        except Exception as e:
            logger.debug(f"获取进程名失败: {e}")
        return ""