import os
import sys


def get_base_path() -> str:
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_icon_path() -> str:
    icon_path = os.path.join(get_base_path(), 'assets', 'icon.ico')
    return icon_path if os.path.exists(icon_path) else ''