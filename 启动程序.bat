@echo off
chcp 65001 >nul
title 错题生成试卷
cd /d "%~dp0"

echo 正在启动错题生成试卷程序...
echo.

REM 尝试使用系统 Python
python -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo 未找到 Python 或 streamlit，请确保已安装 Python 和依赖包
    echo 安装命令：pip install -r requirements.txt
    echo.
    pause
)



