import os
import sys
import shutil

EXCLUDE_MODULES = [
    # PySide6 不需要的模块
    'PySide6.Qt3D', 'PySide6.QtBluetooth', 'PySide6.QtCharts',
    'PySide6.QtDBus', 'PySide6.QtDataVisualization', 'PySide6.QtDesigner',
    'PySide6.QtGraphs', 'PySide6.QtHttpServer', 'PySide6.QtLocation',
    'PySide6.QtMultimedia', 'PySide6.QtMultimediaWidgets', 'PySide6.QtNetworkAuth',
    'PySide6.QtNfc', 'PySide6.QtPdf', 'PySide6.QtPdfWidgets', 'PySide6.QtPositioning',
    'PySide6.QtQuick', 'PySide6.QtQuickWidgets', 'PySide6.QtRemoteObjects',
    'PySide6.QtScxml', 'PySide6.QtSensors', 'PySide6.QtSerialBus',
    'PySide6.QtSerialPort', 'PySide6.QtSpatialAudio', 'PySide6.QtSql',
    'PySide6.QtStateMachine', 'PySide6.QtWebChannel', 'PySide6.QtWebEngine',
    'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets', 'PySide6.QtWebSockets',
    'PySide6.QtWebView', 'PySide6.QtHelp', 'PySide6.QtAxContainer',
    'PySide6.QtOpenGL', 'PySide6.QtOpenGLWidgets', 'PySide6.QtPrintSupport',
    'PySide6.QtTest', 'PySide6.QtUiTools', 'PySide6.QtXml',
    'PySide6.QtNetwork',
    # Python 标准库不需要的大型模块
    'tkinter', 'unittest', 'pydoc', 'doctest', 'test', 'tests',
    'idlelib', 'lib2to3', 'pydoc_data',
    'curses', 'tty', 'pty',
]

FILES_TO_REMOVE = [
    'opengl32sw.dll',
    'Qt6Quick.dll',
    'Qt6Qml.dll',
    'Qt6QmlModels.dll',
    'Qt6Pdf.dll',
    'Qt6Network.dll',
    'Qt6OpenGL.dll',
    'Qt6Svg.dll',
    'QtNetwork.pyd',
]

def build():
    dist_dir = "dist"
    build_dir = "build"
    
    if os.path.exists(dist_dir):
        shutil.rmtree(dist_dir)
    if os.path.exists(build_dir):
        shutil.rmtree(build_dir)
    
    cmd = [
        "pyinstaller",
        "--name=SIS联锁调试助手",
        "--windowed",
        "--onedir",
        "--add-data=config;config",
        "--add-data=data;data",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=sqlite3",
        "--hidden-import=uiautomation",
        "--hidden-import=psutil",
        "--hidden-import=pywinauto",
        "--hidden-import=sqlalchemy",
        "--collect-submodules=sqlalchemy.dialects.sqlite",
        "--strip",
        "--optimize=2",
        "--noconfirm",
    ]
    
    for module in EXCLUDE_MODULES:
        cmd.append(f"--exclude-module={module}")
    
    cmd.append("src/main.py")
    
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("ERROR:", result.stderr)
    
    output_dir = os.path.join(dist_dir, "SIS联锁调试助手", "_internal", "PySide6")
    removed_size = 0
    for filename in FILES_TO_REMOVE:
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            size = os.path.getsize(filepath)
            os.remove(filepath)
            removed_size += size
            print(f"已删除: {filename} ({size/1024/1024:.2f} MB)")
    
    print(f"\n打包完成！输出目录: {dist_dir}/SIS联锁调试助手")
    print(f"已移除不必要的文件，节省约 {removed_size/1024/1024:.2f} MB")

if __name__ == "__main__":
    build()