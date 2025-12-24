"""Streamlit 应用启动脚本，用于打包成 exe"""
import os
import sys
import subprocess
from pathlib import Path

def main():
    """启动 Streamlit 应用"""
    # 获取 exe 所在目录（打包后）
    if getattr(sys, 'frozen', False):
        # 打包后的情况：exe 所在目录
        exe_dir = Path(sys.executable).parent
        app_file = exe_dir / "app.py"
    else:
        # 开发环境：脚本所在目录
        app_dir = Path(__file__).parent
        app_file = app_dir / "app.py"
    
    if not app_file.exists():
        print(f"错误：找不到 app.py 文件")
        print(f"请确保 app.py 与启动程序在同一目录下")
        print(f"当前目录：{Path.cwd()}")
        print(f"查找路径：{app_file}")
        input("\n按回车键退出...")
        return
    
    # 设置工作目录
    os.chdir(app_file.parent)
    
    # 启动 streamlit
    try:
        # 使用 streamlit 模块运行
        import streamlit.web.cli as stcli
        sys.argv = [
            "streamlit",
            "run",
            str(app_file),
            "--server.port=8501",
            "--server.address=localhost",
            "--server.headless=true",
            "--browser.gatherUsageStats=false"
        ]
        stcli.main()
    except ImportError:
        # 如果无法导入 streamlit，尝试命令行方式
        try:
            cmd = [sys.executable, "-m", "streamlit", "run", str(app_file),
                   "--server.port=8501", "--server.address=localhost", "--server.headless=true"]
            subprocess.run(cmd, check=True)
        except FileNotFoundError:
            print("错误：找不到 Python 或 Streamlit")
            print("请确保已安装：pip install streamlit")
            input("按回车键退出...")
        except Exception as e:
            print(f"启动失败：{e}")
            input("按回车键退出...")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        print(f"启动失败：{e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")

if __name__ == "__main__":
    main()



