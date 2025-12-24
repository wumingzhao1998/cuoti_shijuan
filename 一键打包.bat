@echo off
chcp 65001 >nul
title 打包错题生成试卷为 exe
cd /d "%~dp0"

echo ========================================
echo 错题生成试卷 - 打包工具
echo ========================================
echo.

REM 检查是否安装了 PyInstaller
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo [1/3] 正在安装 PyInstaller...
    pip install pyinstaller
    if errorlevel 1 (
        echo 安装 PyInstaller 失败！
        pause
        exit /b 1
    )
    echo.
)

echo [2/3] 正在打包，请稍候...
echo 注意：打包可能需要几分钟，建议使用目录模式（更稳定）
echo.

REM 打包命令（目录模式，更稳定）
pyinstaller --onedir ^
    --windowed ^
    --name="错题生成试卷" ^
    --add-data="app.py;." ^
    --hidden-import=streamlit ^
    --hidden-import=streamlit.web.cli ^
    --hidden-import=docx ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=PIL ^
    --hidden-import=requests ^
    --collect-all=streamlit ^
    --collect-all=docx ^
    run_app.py

REM 如果需要单文件模式，取消下面的注释（不推荐，启动慢且体积大）
REM pyinstaller --onefile ^
REM     --windowed ^
REM     --name="错题生成试卷" ^
REM     --add-data="app.py;." ^
REM     --hidden-import=streamlit ^
REM     --hidden-import=streamlit.web.cli ^
REM     --hidden-import=docx ^
REM     --hidden-import=pandas ^
REM     --hidden-import=numpy ^
REM     --hidden-import=PIL ^
REM     --hidden-import=requests ^
REM     --collect-all=streamlit ^
REM     --collect-all=docx ^
REM     run_app.py

if errorlevel 1 (
    echo.
    echo 打包失败！请检查错误信息。
    pause
    exit /b 1
)

echo.
echo [3/3] 打包完成！
echo.
echo exe 文件位置：dist\错题生成试卷.exe
echo.
echo 提示：首次运行 exe 可能需要几秒钟加载时间
echo.

pause



