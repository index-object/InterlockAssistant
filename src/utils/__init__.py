import os


def get_icon_path() -> str:
    icon_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'assets', 'icon.ico')
    return icon_path if os.path.exists(icon_path) else ''