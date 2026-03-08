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
        self._timer = None
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
        
        if self._timer:
            self._timer.stop()
        
        self._timer = QTimer()
        self._timer.timeout.connect(self._poll_data)
        self._timer.start(self._polling_interval)
        
        self._poll_data()
    
    def stop_watching(self):
        logger.info("停止监控窗口")
        if self._timer:
            self._timer.stop()
            self._timer = None
        
        self._current_hwnd = None
        self._window = None
        self._last_value = None
    
    def _poll_data(self):
        if not self._current_hwnd:
            return
        
        try:
            value = self._read_target_value()
            
            if value and value != self._last_value:
                logger.info(f"检测到数据变化: {value}")
                self._last_value = value
                self.data_changed.emit(value)
        except Exception as e:
            logger.error(f"轮询数据失败: {e}")
    
    def _read_target_value(self):
        try:
            import uiautomation as auto
            
            window = auto.ControlFromHandle(self._current_hwnd)
            if not window:
                logger.debug(f"无法获取窗口控件: hwnd={self._current_hwnd}")
                return None
            
            target_config = self._config['target_window']['target_control']
            parent_class = target_config.get('parent_class', 'QTreeWidget')
            name_pattern = target_config.get('name_pattern', r'Set Value:\s*(.+)')
            
            tree_widget = window.Control(control_type='TreeControl', class_name=parent_class)
            if not tree_widget:
                logger.debug(f"未找到TreeWidget控件")
                return None
            
            tree_items = tree_widget.GetChildren()
            
            for item in tree_items:
                try:
                    name = item.Name
                    if name and 'Set Value:' in name:
                        match = re.search(name_pattern, name)
                        if match:
                            value = match.group(1).strip()
                            logger.debug(f"提取到值: {value}")
                            return value
                except Exception as e:
                    logger.debug(f"处理TreeItem时出错: {e}")
                    continue
            
            logger.debug("未找到匹配的TreeItem")
            return None
            
        except Exception as e:
            logger.error(f"读取目标值失败: {e}")
            return None
    
    def is_target_window(self, title, process_name):
        if not self._config:
            return False
        
        target_config = self._config['target_window']
        target_title = target_config.get('title', '')
        target_process = target_config.get('process_name', '')
        
        return title == target_title and process_name == target_process