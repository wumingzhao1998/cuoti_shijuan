@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 推送到 GitHub
echo ========================================
echo.

echo [1/5] 检查 Git 状态...
git status
if errorlevel 1 (
    echo 错误：Git 未初始化或不在 Git 仓库中
    echo 正在初始化 Git 仓库...
    git init
    git remote add origin https://github.com/wumingzhao1998/cuoti_shijuan.git 2>nul
)

echo.
echo [2/5] 添加所有更改的文件...
git add .
if errorlevel 1 (
    echo 错误：添加文件失败
    pause
    exit /b 1
)

echo.
echo [3/5] 提交更改...
git commit -m "优化 Streamlit Cloud 部署兼容性：改进配置文件写入错误处理"
if errorlevel 1 (
    echo 警告：提交可能失败（没有更改或已提交）
)

echo.
echo [4/5] 检查远程仓库...
git remote -v
if errorlevel 1 (
    echo 添加远程仓库...
    git remote add origin https://github.com/wumingzhao1998/cuoti_shijuan.git
)

echo.
echo [5/5] 推送到 GitHub...
git push -u origin main 2>nul
if errorlevel 1 (
    echo 尝试推送到 master 分支...
    git push -u origin master 2>nul
    if errorlevel 1 (
        echo 错误：推送失败
        echo 请检查：
        echo 1. 是否已配置 GitHub 认证
        echo 2. 网络连接是否正常
        echo 3. 仓库权限是否正确
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo 推送完成！
echo ========================================
echo.
pause

