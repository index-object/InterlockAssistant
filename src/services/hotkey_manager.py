import json
import os
import sys


def _get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class HotkeyManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(_get_base_path(), 'config', 'config.json')
        self.config_path = config_path
        self.hotkeys = {}
        self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    hotkey_config = config.get('hotkey', {})
                    self.hotkeys = {'show_hide': hotkey_config.get('show_hide', 'Ctrl+Shift+Z')}
            else:
                self.hotkeys = {'show_hide': 'Ctrl+Shift+Z'}
        except (FileNotFoundError, json.JSONDecodeError):
            self.hotkeys = {'show_hide': 'Ctrl+Shift+Z'}
    
    def save_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}
        
        if 'hotkey' not in config:
            config['hotkey'] = {}
        config['hotkey']['show_hide'] = self.hotkeys.get('show_hide', 'Ctrl+Shift+Z')
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    def set_hotkey(self, name: str, hotkey: str):
        self.hotkeys[name] = hotkey
        self.save_config()
    
    def get_hotkey(self, name: str) -> str:
        return self.hotkeys.get(name, 'Ctrl+Shift+Z')
    
    def get_all_hotkeys(self) -> dict:
        return self.hotkeys.copy()