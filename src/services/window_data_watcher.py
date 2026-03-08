import json
import logging
import re
import time
from pathlib import Path
from PySide6.QtCore import QObject, Signal, QTimer

logger = logging.getLogger(__name__)


class WindowDataWatcher(QObject):
    data_changed = Signal(str)
    
    def __init__(self):
        super().__init__()
        self._config = None
        self._current_hwnd = None
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll_data)
        self._last_value = None
        self._automation = None
        self._window = None
        self._polling_interval = 500
        
        self._load_config()
    
    def _load_config(self):
        config_path = Path("config/target_window.json")
        if not config_path.exists():
            logger.error(f"配置文件不存在: {config_path}")
            return
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                self._config = json.load(f)
            logger.info(f"加载目标窗口配置: {self._config}")
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
    
    def start_watching(self, hwnd):
        if not self._config:
            logger.error("未加载配置，无法开始监控")
            return
        
        logger.info(f"开始监控窗口: hwnd={hwnd}")
        self._current_hwnd = hwnd
        self._last_value = None
        
        self._timer.start(self._polling_interval)
        logger.info(f"定时器已启动，间隔: {self._polling_interval}ms")
        
        self._poll_data()
    
    def stop_watching(self):
        logger.info("停止监控窗口")
        self._timer.stop()
        
        self._current_hwnd = None
        self._window = None
        self._last_value = None
    
    def _poll_data(self):
        if not self._current_hwnd:
            logger.warning("轮询数据时 hwnd 为空")
            return
        
        try:
            value = self._read_target_value()
            
            if value is None:
                logger.info("未能读取到目标值")
            elif value != self._last_value:
                logger.info(f"检测到数据变化: {value}")
                self._last_value = value
                self.data_changed.emit(value)
            else:
                logger.debug(f"数据未变化: {value}")
        except Exception as e:
            logger.error(f"轮询数据失败: {e}", exc_info=True)
    
    def _read_target_value(self):
        try:
            import uiautomation as auto
            
            logger.info(f"尝试读取窗口数据: hwnd={self._current_hwnd}")
            window = auto.ControlFromHandle(self._current_hwnd)
            if not window:
                logger.info(f"无法获取窗口控件: hwnd={self._current_hwnd}")
                return None
            
            target_config = self._config['target_window']['target_control']
            name_pattern = target_config.get('name_pattern', r'Set Value:\s*(.+)')
            
            logger.info("递归遍历所有控件，查找Set Value:")
            value = self._find_value_recursive(window, name_pattern, 0)
            if value:
                logger.info(f"找到目标值: {value}")
                return value
            
            logger.info("未能找到目标值")
            return None
            
        except Exception as e:
            logger.error(f"读取目标值失败: {e}", exc_info=True)
            return None
    
    def _find_value_recursive(self, control, name_pattern, depth):
        if depth > 20:
            return None
        
        try:
            name = getattr(control, 'Name', None)
            if name and 'Set Value:' in str(name):
                match = re.search(name_pattern, str(name))
                if match:
                    logger.info(f"找到匹配项: {name}")
                    return match.group(1).strip()
        except Exception:
            pass
        
        try:
            children = control.GetChildren()
            if children:
                for child in children:
                    result = self._find_value_recursive(child, name_pattern, depth + 1)
                    if result:
                        return result
        except Exception:
            pass
        
        return None
    
    def is_target_window(self, title, process_name):
        if not self._config:
            return False
        
        target_config = self._config['target_window']
        target_title = target_config.get('title', '')
        target_process = target_config.get('process_name', '')
        
        return title == target_title and process_name == target_process