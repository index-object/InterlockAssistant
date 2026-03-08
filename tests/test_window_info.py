import pytest
from src.services.window_info import WindowInfo

def test_get_foreground_window():
    info = WindowInfo()
    hwnd = info.get_foreground_window()
    assert hwnd is not None
    assert hwnd >= 0

def test_get_window_title():
    info = WindowInfo()
    title = info.get_window_title()
    assert isinstance(title, str)

def test_should_monitor_no_filters():
    info = WindowInfo()
    assert info.should_monitor([]) is True

def test_should_monitor_with_filters():
    info = WindowInfo()
    original_get_text = info.get_window_text
    info.get_window_text = lambda hwnd=None: "Notepad++ - test.txt"
    assert info.should_monitor(["Notepad++"]) is True
    assert info.should_monitor(["VS Code"]) is False
    info.get_window_text = original_get_text

def test_get_all_windows():
    info = WindowInfo()
    windows = info.get_all_windows()
    assert isinstance(windows, list)