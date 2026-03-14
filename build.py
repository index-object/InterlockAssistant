import os
import sys
import shutil

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
"--add-data=src;src",
        "--add-data=config;config",
        "--add-data=data;data",
        "--hidden-import=PySide6",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=sqlite3",
        "--hidden-import=uiautomation",
        "--hidden-import=psutil",
        "--hidden-import=pywinauto",
        "--hidden-import=sqlalchemy",
        "--collect-submodules=PySide6.QtCore",
        "--collect-submodules=PySide6.QtWidgets",
        "--collect-submodules=PySide6.QtGui",
        "--collect-submodules=shiboken6",
        "--collect-submodules=sqlalchemy.dialects.sqlite",
        "--exclude-module=PySide6.Qt3D",
        "--exclude-module=PySide6.QtBluetooth",
        "--exclude-module=PySide6.QtCharts",
        "--exclude-module=PySide6.QtDBus",
        "--exclude-module=PySide6.QtDataVisualization",
        "--exclude-module=PySide6.QtDesigner",
        "--exclude-module=PySide6.QtGraphs",
        "--exclude-module=PySide6.QtHttpServer",
        "--exclude-module=PySide6.QtLocation",
        "--exclude-module=PySide6.QtMultimedia",
        "--exclude-module=PySide6.QtNetworkAuth",
        "--exclude-module=PySide6.QtNfc",
        "--exclude-module=PySide6.QtPdf",
        "--exclude-module=PySide6.QtPositioning",
        "--exclude-module=PySide6.QtQuick",
        "--exclude-module=PySide6.QtRemoteObjects",
        "--exclude-module=PySide6.QtScxml",
        "--exclude-module=PySide6.QtSensors",
        "--exclude-module=PySide6.QtSerialBus",
        "--exclude-module=PySide6.QtSerialPort",
        "--exclude-module=PySide6.QtSpatialAudio",
        "--exclude-module=PySide6.QtSql",
        "--exclude-module=PySide6.QtStateMachine",
        "--exclude-module=PySide6.QtWebChannel",
        "--exclude-module=PySide6.QtWebEngine",
        "--exclude-module=PySide6.QtWebSockets",
        "--exclude-module=PySide6.QtWebView",
        "--exclude-module=PySide6.QtHelp",
        "--exclude-module=PySide6.QtAxContainer",
        "--noconfirm",
        "src/main.py"
    ]
    
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("ERROR:", result.stderr)
    
    print(f"\n打包完成！输出目录: {dist_dir}/SIS联锁调试助手")

if __name__ == "__main__":
    build()