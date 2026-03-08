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
        "--name=剪贴板监视助手",
        "--windowed",
        "--onedir",
        "--add-data=src;src",
        "--hidden-import=PySide2",
        "--hidden-import=win32clipboard",
        "--hidden-import=win32gui",
        "--hidden-import=sqlite3",
        "--collect-all=PySide2",
        "--collect-all=shiboken2",
        "--noconfirm",
        "src/main.py"
    ]
    
    import subprocess
    result = subprocess.run(cmd, capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("ERROR:", result.stderr)
    
    print(f"\n打包完成！输出目录: {dist_dir}/剪贴板监视助手")

if __name__ == "__main__":
    build()