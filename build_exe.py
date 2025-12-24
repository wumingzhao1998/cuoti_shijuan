"""打包脚本：使用 PyInstaller 打包成 exe"""
import PyInstaller.__main__
import sys
from pathlib import Path

def build():
    app_dir = Path(__file__).parent
    
    PyInstaller.__main__.run([
        'run_app.py',
        '--name=错题生成试卷',
        '--onefile',
        '--windowed',  # Windows下隐藏控制台窗口
        '--icon=NONE',  # 可以添加图标文件路径
        '--add-data=app.py;.',
        '--hidden-import=streamlit',
        '--hidden-import=streamlit.web.cli',
        '--hidden-import=docx',
        '--hidden-import=pandas',
        '--hidden-import=numpy',
        '--hidden-import=PIL',
        '--hidden-import=requests',
        '--collect-all=streamlit',
        '--collect-all=docx',
    ])
    
    print("\n打包完成！可执行文件在 dist 目录中")

if __name__ == "__main__":
    try:
        build()
    except Exception as e:
        print(f"打包失败：{e}")
        input("按回车键退出...")



