# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = ['PySide6', 'PySide6.QtWidgets', 'PySide6.QtCore', 'PySide6.QtGui', 'win32clipboard', 'win32gui', 'sqlite3']
hiddenimports += collect_submodules('PySide6.QtCore')
hiddenimports += collect_submodules('PySide6.QtWidgets')
hiddenimports += collect_submodules('PySide6.QtGui')
hiddenimports += collect_submodules('shiboken6')


a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src'), ('config', 'config')],
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.Qt3D', 'PySide6.QtBluetooth', 'PySide6.QtCharts', 'PySide6.QtDBus', 'PySide6.QtDataVisualization', 'PySide6.QtDesigner', 'PySide6.QtGraphs', 'PySide6.QtHttpServer', 'PySide6.QtLocation', 'PySide6.QtMultimedia', 'PySide6.QtNetworkAuth', 'PySide6.QtNfc', 'PySide6.QtPdf', 'PySide6.QtPositioning', 'PySide6.QtQuick', 'PySide6.QtRemoteObjects', 'PySide6.QtScxml', 'PySide6.QtSensors', 'PySide6.QtSerialBus', 'PySide6.QtSerialPort', 'PySide6.QtSpatialAudio', 'PySide6.QtSql', 'PySide6.QtStateMachine', 'PySide6.QtWebChannel', 'PySide6.QtWebEngine', 'PySide6.QtWebSockets', 'PySide6.QtWebView', 'PySide6.QtHelp', 'PySide6.QtAxContainer'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='剪贴板监视助手',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='剪贴板监视助手',
)
