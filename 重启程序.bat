@echo off
chcp 65001 >nul
title 重启错题生成试卷程序
cd /d "%~dp0"

echo 正在停止旧进程...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *streamlit*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo 正在启动新程序...
echo.
python -m streamlit run app.py

if errorlevel 1 (
    echo.
    echo 启动失败，请检查错误信息
    pause
)
