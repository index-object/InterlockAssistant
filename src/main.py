import sys
import json
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QShortcut
from PySide2.QtCore import Qt
from PySide2.QtGui import QKeySequence, QPixmap

from src.services.clipboard_watcher import ClipboardWatcher
from src.services.window_info import WindowInfo
from src.services.database_service import DatabaseService
from src.services.hotkey_manager import HotkeyManager
from src.ui.floating_window import FloatingWindow


class ClipboardMonitorApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.clipboard_watcher = ClipboardWatcher()
        self.window_info = WindowInfo()
        self.database_service = DatabaseService('data/keywords.db')
        self.hotkey_manager = HotkeyManager()
        
        self.floating_window = FloatingWindow(
            self.clipboard_watcher,
            self.window_info,
            self.database_service
        )
        self.floating_window.move_to_corner()
        
        self.create_tray()
        self.setup_shortcut()
        
        self.clipboard_watcher.clipboard_changed.connect(self.on_clipboard_change)
        self.clipboard_watcher.start()
        
        self.floating_window.show()
    
    def create_tray(self):
        self.tray = QSystemTrayIcon()
        self.tray.setToolTip("剪贴板监视")
        
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.blue)
        self.tray.setIcon(pixmap)
        
        menu = QMenu()
        menu.addAction("显示/隐藏", self.toggle_window)
        menu.addAction("配置", self.open_config)
        menu.addAction("退出", self.quit_app)
        self.tray.setContextMenu(menu)
        
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()
    
    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
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
    
    def on_clipboard_change(self, text):
        if not text:
            return
        
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                filters = config.get('window_filters', [])
        except:
            filters = []
        
        title = self.window_info.get_window_title()
        
        if filters and not self.window_info.should_monitor(filters):
            return
        
        self.floating_window.update_title(title)
        self.floating_window.update_content(text)
    
    def open_config(self):
        from src.ui.config_window import ConfigWindow
        config = ConfigWindow(self.database_service, self.hotkey_manager)
        config.exec_()
    
    def quit_app(self):
        self.clipboard_watcher.stop()
        self.app.quit()
    
    def run(self):
        sys.exit(self.app.exec_())


if __name__ == "__main__":
    app = ClipboardMonitorApp()
    app.run()