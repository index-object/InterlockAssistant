import sys
import json
import logging
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QFileDialog
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QPixmap, QShortcut

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from src.services.window_data_watcher import WindowDataWatcher
from src.services.window_info import WindowInfo
from src.services.database_service import DatabaseService
from src.services.hotkey_manager import HotkeyManager
from src.services.window_focus_watcher import WindowFocusWatcher
from src.services.ui_automation_reader import UIAutomationReader
from src.services.window_detector import WindowDetector
from src.services.window_picker import WindowPicker
from src.ui.floating_window import FloatingWindow
from src.ui.window_detector_window import WindowDetectorWindow


class WindowMonitorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.window_data_watcher = WindowDataWatcher()
        self.window_info = WindowInfo()
        self.database_service = DatabaseService('data/keywords.db')
        self.hotkey_manager = HotkeyManager()
        self.window_focus_watcher = WindowFocusWatcher()
        self.ui_reader = UIAutomationReader()
        self.window_detector = WindowDetector()
        self.window_picker = WindowPicker()
        self.window_detector_window = None
        
        self.test_mode = False
        self.test_input_dialog = None
        
        self.floating_window = FloatingWindow(
            self.window_info,
            self.database_service
        )
        self.floating_window.move_to_corner()
        
        self.create_tray()
        self.setup_shortcut()
        
        self.window_data_watcher.data_changed.connect(self.on_data_change)
        
        self.window_focus_watcher.window_focused.connect(self.on_window_focus)
        
        self.start_window_monitor()
        
        self.floating_window.show()
    
    def start_window_monitor(self):
        self.window_focus_watcher.set_target_windows(['Item Properties'])
        self.window_focus_watcher.start()
        logger.info("窗口焦点监控已启动")
    
    def on_window_focus(self, hwnd, class_name, window_title):
        logger.info(f"检测到焦点变化: class_name={class_name}, hwnd={hwnd}")
        logger.info(f"窗口标题: {window_title}")
        
        process_name = self._get_process_name(hwnd)
        logger.info(f"进程名: {process_name}")
        
        if self.window_data_watcher.is_target_window(window_title, process_name):
            logger.info(f"匹配目标窗口，开始监控")
            self.floating_window.update_title(f"[监控] {window_title}")
            self.window_data_watcher.start_watching(hwnd)
        else:
            logger.info(f"不匹配目标窗口，停止监控")
            self.window_data_watcher.stop_watching()
    
    def _get_process_name(self, hwnd):
        try:
            import psutil
            import ctypes
            
            pid = ctypes.c_ulong()
            ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            
            if pid.value:
                process = psutil.Process(pid.value)
                return process.name()
        except Exception as e:
            logger.error(f"获取进程名失败: {e}")
        return ""
    
    def on_data_change(self, value):
        logger.info(f"检测到数据变化: {value}")
        
        self.floating_window.update_title("Item Properties")
        self.floating_window.update_content(value)
    
    def create_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("窗口数据监控")
        
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.GlobalColor.blue)
        self.tray.setIcon(pixmap)
        
        menu = QMenu()
        menu.addAction("显示/隐藏", self.toggle_window)
        menu.addAction("窗口检测器", self.open_window_detector)
        self.test_mode_action = menu.addAction("测试模式", self.toggle_test_mode)
        self.test_mode_action.setCheckable(True)
        self.test_mode_action.setChecked(False)
        menu.addAction("配置", self.open_config)
        menu.addAction("导入IO数据", self.import_io_data)
        menu.addAction("退出", self.quit_app)
        self.tray.setContextMenu(menu)
        
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.toggle_window()
    
    def toggle_window(self):
        if self.floating_window.isVisible():
            self.floating_window.hide()
        else:
            self.floating_window.show()
    
    def setup_shortcut(self):
        hotkey_str = self.hotkey_manager.get_hotkey('show_hide')
        self.show_hide_shortcut = QShortcut(
            QKeySequence(hotkey_str),
            self.floating_window
        )
        self.show_hide_shortcut.activated.connect(self.toggle_window)
    
    def open_config(self):
        from src.ui.config_window import ConfigWindow
        config = ConfigWindow()
        if config.exec():
            self.hotkey_manager.load_config()
            self.setup_shortcut()
    
    def import_io_data(self):
        files, _ = QFileDialog.getOpenFileNames(
            None,
            "选择要导入的CSV文件",
            "",
            "CSV文件 (*.csv *.CSV);;所有文件 (*)"
        )

        if not files:
            return

        total_result = {'iodisc': 0, 'ioreal': 0, 'ioint': 0, 'ioaccess': 0, 'errors': []}

        for i, csv_file in enumerate(files):
            try:
                mode = 'replace' if i == 0 else 'merge'
                result = self.database_service.import_from_csv(csv_file, mode=mode)
                total_result['iodisc'] += result.iodisc_count
                total_result['ioreal'] += result.ioreal_count
                total_result['ioint'] += result.ioint_count
                total_result['ioaccess'] += result.ioaccess_count
                if result.errors:
                    total_result['errors'].extend(result.errors)
            except Exception as e:
                total_result['errors'].append(f"{csv_file}: {str(e)}")

        if total_result['errors']:
            self.tray.showMessage(
                "导入失败",
                f"错误: {', '.join(total_result['errors'][:3])}",
                QSystemTrayIcon.MessageIcon.Critical,
                5000
            )
        else:
            self.tray.showMessage(
                "导入完成",
                f"IODisc: {total_result['iodisc']} 条\n"
                f"IOReal: {total_result['ioreal']} 条\n"
                f"IOInt: {total_result['ioint']} 条\n"
                f"IOAccess: {total_result['ioaccess']} 条",
                QSystemTrayIcon.MessageIcon.Information,
                5000
            )
    
    def open_window_detector(self):
        try:
            logger.info("正在打开窗口检测器...")
            if self.window_detector_window is None:
                logger.info("创建窗口检测器实例...")
                self.window_detector_window = WindowDetectorWindow(
                    self.window_detector,
                    self.window_picker
                )
                logger.info("窗口检测器实例创建成功")
            logger.info("显示窗口检测器...")
            self.window_detector_window.show()
            self.window_detector_window.raise_()
            logger.info("窗口检测器已显示")
        except Exception as e:
            logger.error(f"打开窗口检测器失败: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
    
    def toggle_test_mode(self):
        self.test_mode = not self.test_mode
        self.test_mode_action.setChecked(self.test_mode)
        
        if self.test_mode:
            logger.info("测试模式已开启")
            self.floating_window.update_title("[测试模式] 请输入测试值")
            self.window_data_watcher.stop_watching()
            self.window_focus_watcher.stop()
            self.open_test_input_dialog()
        else:
            logger.info("测试模式已关闭")
            self.floating_window.update_title("等待数据...")
            self.floating_window.update_content("")
            self.start_window_monitor()
    
    def open_test_input_dialog(self):
        from src.ui.test_input_dialog import TestInputDialog
        
        if self.test_input_dialog is None:
            self.test_input_dialog = TestInputDialog()
            self.test_input_dialog.value_submitted.connect(self.on_test_value_submitted)
        
        self.test_input_dialog.show()
        self.test_input_dialog.raise_()
        self.test_input_dialog.activateWindow()
    
    def on_test_value_submitted(self, value):
        logger.info(f"测试模式收到输入: {value}")
        self.floating_window.update_content(value)
    
    def quit_app(self):
        self.window_data_watcher.stop_watching()
        self.window_focus_watcher.stop()
        self.app.quit()
    
    def run(self):
        sys.exit(self.app.exec())


if __name__ == "__main__":
    app = WindowMonitorApp()
    app.run()