import pytest
import os
import tempfile
import json
from src.services.hotkey_manager import HotkeyManager

@pytest.fixture
def temp_config():
    fd, path = tempfile.mkstemp(suffix='.json')
    os.close(fd)
    yield path
    os.unlink(path)

def test_hotkey_manager_init(temp_config):
    manager = HotkeyManager(temp_config)
    assert manager is not None
    assert 'show_hide' in manager.hotkeys

def test_set_hotkey(temp_config):
    manager = HotkeyManager(temp_config)
    manager.set_hotkey('show_hide', 'Ctrl+Alt+V')
    assert manager.get_hotkey('show_hide') == 'Ctrl+Alt+V'

def test_get_hotkey_default(temp_config):
    manager = HotkeyManager(temp_config)
    result = manager.get_hotkey('nonexistent')
    assert result == 'Ctrl+Shift+V'

def test_save_config(temp_config):
    manager = HotkeyManager(temp_config)
    manager.set_hotkey('custom', 'Ctrl+K')
    
    with open(temp_config, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    assert config['hotkeys']['custom'] == 'Ctrl+K'