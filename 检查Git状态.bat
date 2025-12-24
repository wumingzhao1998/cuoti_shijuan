@echo off
chcp 65001 >nul
title 检查Git状态
cd /d "%~dp0"

echo ========================================
echo 检查Git配置和状态
echo ========================================
echo.

echo [1] 检查Git是否安装...
git --version
if errorlevel 1 (
    echo 错误：Git未安装或未添加到PATH
    pause
    exit /b 1
)
echo.

echo [2] 检查是否已初始化Git仓库...
if exist .git (
    echo ✓ Git仓库已初始化
) else (
    echo ✗ Git仓库未初始化
    echo 正在初始化...
    git init
)
echo.

echo [3] 检查远程仓库配置...
git remote -v
if errorlevel 1 (
    echo 警告：未配置远程仓库
    echo 正在添加远程仓库...
    git remote add origin https://github.com/cuoti_shijuan/cuoti_shijuan.git
)
echo.

echo [4] 检查当前分支...
git branch
echo.

echo [5] 检查Git用户配置...
git config user.name
git config user.email
echo.

echo [6] 检查待提交的文件...
git status
echo.

echo [7] 检查是否有未提交的更改...
git diff --stat
echo.

echo [8] 检查标签...
git tag
echo.

echo ========================================
echo 诊断信息
echo ========================================
echo.

echo 检查GitHub认证方式...
git config --get credential.helper
echo.

echo 检查远程仓库连接...
git ls-remote origin 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️ 无法连接到远程仓库，可能的原因：
    echo 1. 远程仓库不存在
    echo 2. 未配置GitHub认证
    echo 3. 网络连接问题
    echo.
    echo 解决方案：
    echo 1. 确保GitHub上已创建仓库：https://github.com/cuoti_shijuan/cuoti_shijuan
    echo 2. 配置GitHub认证（SSH密钥或Personal Access Token）
    echo 3. 检查网络连接
)
echo.

pause
