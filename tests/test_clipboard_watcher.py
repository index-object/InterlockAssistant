import pytest
import time
from src.services.clipboard_watcher import ClipboardWatcher

def test_clipboard_watcher_init():
    watcher = ClipboardWatcher()
    assert watcher is not None
    assert watcher.last_content == ""

def test_clipboard_watcher_start_stop():
    watcher = ClipboardWatcher()
    watcher.start()
    assert watcher._running is True
    watcher.stop()
    assert watcher._running is False