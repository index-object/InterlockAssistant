import json
import os

class HotkeyManager:
    def __init__(self, config_path: str = "config.json"):
        self.config_path = config_path
        self.hotkeys = {}
        self.load_config()
    
    def load_config(self):
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.hotkeys = config.get('hotkeys', {})
            else:
                self.hotkeys = {'show_hide': 'Ctrl+Shift+V'}
                self.save_config()
        except (FileNotFoundError, json.JSONDecodeError):
            self.hotkeys = {'show_hide': 'Ctrl+Shift+V'}
    
    def save_config(self):
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {}
        config['hotkeys'] = self.hotkeys
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    
    def set_hotkey(self, name: str, hotkey: str):
        self.hotkeys[name] = hotkey
        self.save_config()
    
    def get_hotkey(self, name: str) -> str:
        return self.hotkeys.get(name, 'Ctrl+Shift+V')
    
    def get_all_hotkeys(self) -> dict:
        return self.hotkeys.copy()