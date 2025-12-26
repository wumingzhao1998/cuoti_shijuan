@echo off
chcp 65001 >nul
title 修复并推送到GitHub
cd /d "%~dp0"

echo ========================================
echo 修复Git配置并推送到GitHub
echo ========================================
echo.

:: 确保仓库初始化
if not exist .git (
    echo 初始化Git仓库...
    git init
)

:: 确保远程仓库配置
git remote remove origin 2>nul
git remote add origin https://github.com/wumingzhao1998/cuoti_shijuan.git

:: 确保有分支
git checkout -b main 2>nul || git checkout main 2>nul || git branch -M main 2>nul

:: 添加所有文件
echo 添加文件...
git add .

:: 提交
echo 提交更改...
git commit -m "发布 v1.0 版本" --allow-empty

:: 创建标签
echo 创建标签...
git tag -d v1.0 2>nul
git tag -a v1.0 -m "版本 v1.0 - 初始发布版本"

echo.
echo ========================================
echo 准备推送
echo ========================================
echo.
echo 重要提示：
echo 1. 如果使用HTTPS，推送时需要输入GitHub用户名和Personal Access Token
echo 2. 如果使用SSH，确保已配置SSH密钥
echo.
echo 如果遇到认证问题，可以：
echo - 使用Personal Access Token（在GitHub Settings ^> Developer settings ^> Personal access tokens创建）
echo - 或切换到SSH：git remote set-url origin git@github.com:cuoti_shijuan/cuoti_shijuan.git
echo.
pause

echo.
echo 正在推送代码...
git push -u origin main
if errorlevel 1 (
    echo.
    echo 推送失败，尝试其他方式...
    echo.
    echo 选项1：使用SSH（如果已配置SSH密钥）
    echo   git remote set-url origin git@github.com:cuoti_shijuan/cuoti_shijuan.git
    echo   git push -u origin main
    echo.
    echo 选项2：使用Personal Access Token
    echo   推送时，用户名输入GitHub用户名，密码输入Personal Access Token
    echo.
    echo 选项3：检查仓库是否存在
    echo   访问 https://github.com/new 创建 cuoti_shijuan 仓库
    echo.
    pause
    exit /b 1
)

echo.
echo 正在推送标签...
git push origin v1.0
if errorlevel 1 (
    echo 警告：标签推送失败，可以稍后手动推送
    echo 命令：git push origin v1.0
) else (
    echo ✓ 标签推送成功
)

echo.
echo ========================================
echo ✓ 推送完成！
echo ========================================
echo.
echo 仓库地址：https://github.com/wumingzhao1998/cuoti_shijuan
echo 标签地址：https://github.com/wumingzhao1998/cuoti_shijuan/releases/tag/v1.0
echo.
pause

