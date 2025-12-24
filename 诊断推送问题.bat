@echo off
chcp 65001 >nul
title 诊断GitHub推送问题
cd /d "%~dp0"

echo ========================================
echo GitHub推送问题诊断工具
echo ========================================
echo.

:: 1. 检查Git是否安装
echo [1/8] 检查Git安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Git未安装或未添加到PATH
    echo 请先安装Git: https://git-scm.com/download/win
    pause
    exit /b 1
) else (
    echo ✓ Git已安装
    git --version
)
echo.

:: 2. 检查仓库初始化
echo [2/8] 检查Git仓库...
if not exist .git (
    echo ✗ Git仓库未初始化
    echo 正在初始化...
    git init
    if errorlevel 1 (
        echo ✗ 初始化失败
        pause
        exit /b 1
    )
    echo ✓ 已初始化
) else (
    echo ✓ Git仓库已存在
)
echo.

:: 3. 检查远程仓库配置
echo [3/8] 检查远程仓库配置...
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo ✗ 未配置远程仓库
    echo 正在添加远程仓库...
    git remote add origin https://github.com/cuoti_shijuan/cuoti_shijuan.git
    if errorlevel 1 (
        echo ✗ 添加远程仓库失败
    ) else (
        echo ✓ 已添加远程仓库
    )
) else (
    echo ✓ 远程仓库已配置
    git remote get-url origin
)
echo.

:: 4. 检查Git用户配置
echo [4/8] 检查Git用户配置...
set GIT_USER_NAME=
set GIT_USER_EMAIL=
for /f "tokens=*" %%i in ('git config user.name 2^>nul') do set GIT_USER_NAME=%%i
for /f "tokens=*" %%i in ('git config user.email 2^>nul') do set GIT_USER_EMAIL=%%i

if "%GIT_USER_NAME%"=="" (
    echo ⚠️ 未配置Git用户名
    echo 请输入Git用户名（用于提交记录）：
    set /p GIT_USER_NAME="用户名: "
    git config user.name "%GIT_USER_NAME%"
)

if "%GIT_USER_EMAIL%"=="" (
    echo ⚠️ 未配置Git邮箱
    echo 请输入Git邮箱（用于提交记录）：
    set /p GIT_USER_EMAIL="邮箱: "
    git config user.email "%GIT_USER_EMAIL%"
)

if not "%GIT_USER_NAME%"=="" echo ✓ 用户名: %GIT_USER_NAME%
if not "%GIT_USER_EMAIL%"=="" echo ✓ 邮箱: %GIT_USER_EMAIL%
echo.

:: 5. 检查当前分支
echo [5/8] 检查当前分支...
git branch --show-current >nul 2>&1
if errorlevel 1 (
    echo ⚠️ 当前没有分支，正在创建main分支...
    git checkout -b main 2>nul
    if errorlevel 1 (
        echo 尝试创建master分支...
        git checkout -b master 2>nul
    )
)
git branch
echo.

:: 6. 检查待提交的文件
echo [6/8] 检查文件状态...
git status --short
echo.

:: 7. 测试远程仓库连接
echo [7/8] 测试远程仓库连接...
echo 正在连接GitHub...
git ls-remote origin >nul 2>&1
if errorlevel 1 (
    echo.
    echo ✗ 无法连接到远程仓库
    echo.
    echo 可能的原因：
    echo 1. 远程仓库不存在
    echo    解决方案：访问 https://github.com/new 创建 cuoti_shijuan 仓库
    echo.
    echo 2. 未配置GitHub认证
    echo    解决方案A（推荐）：使用SSH
    echo      - 生成SSH密钥：ssh-keygen -t ed25519 -C "your_email@example.com"
    echo      - 添加公钥到GitHub：Settings ^> SSH and GPG keys
    echo      - 使用SSH地址：git remote set-url origin git@github.com:cuoti_shijuan/cuoti_shijuan.git
    echo.
    echo    解决方案B：使用Personal Access Token
    echo      - 访问：https://github.com/settings/tokens
    echo      - 生成新token（勾选repo权限）
    echo      - 推送时使用token作为密码
    echo.
    echo 3. 网络连接问题
    echo    检查网络连接和防火墙设置
    echo.
) else (
    echo ✓ 可以连接到远程仓库
)
echo.

:: 8. 检查认证方式
echo [8/8] 检查认证配置...
git config --get credential.helper
if errorlevel 1 (
    echo ⚠️ 未配置凭据助手
    echo 提示：Windows可以使用Git Credential Manager
    echo 安装命令：git config --global credential.helper manager-core
)
echo.

echo ========================================
echo 诊断完成
echo ========================================
echo.

echo 如果所有检查都通过，可以尝试推送：
echo   git push -u origin main
echo.
echo 如果推送时提示认证失败，请：
echo 1. 使用Personal Access Token作为密码
echo 2. 或配置SSH密钥
echo.

pause
