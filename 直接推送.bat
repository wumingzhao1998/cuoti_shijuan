@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo 正在初始化Git...
git init >nul 2>&1

echo 正在配置远程仓库...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/wumingzhao1998/cuoti_shijuan.git

echo 正在创建main分支...
git checkout -b main >nul 2>&1 || git branch -M main >nul 2>&1

echo 正在添加文件...
git add .

echo 正在提交...
git commit -m "发布 v1.0 版本" --allow-empty

echo 正在创建标签...
git tag -d v1.0 >nul 2>&1
git tag -a v1.0 -m "版本 v1.0" >nul 2>&1

echo.
echo ========================================
echo 准备推送到GitHub
echo ========================================
echo.
echo 推送时需要输入GitHub认证信息：
echo - 用户名：输入你的GitHub用户名
echo - 密码：输入Personal Access Token（不是GitHub密码）
echo.
echo 如果还没有Token，请访问：
echo https://github.com/settings/tokens
echo.
pause

echo.
echo 正在推送代码...
git push -u origin main
if errorlevel 1 (
    echo.
    echo 推送失败！请检查：
    echo 1. 是否已创建仓库：https://github.com/wumingzhao1998/cuoti_shijuan
    echo 2. 是否已配置Personal Access Token
    echo 3. 网络连接是否正常
    pause
    exit /b 1
)

echo.
echo 正在推送标签...
git push origin v1.0

echo.
echo ========================================
echo 推送完成！
echo ========================================
echo.
echo 仓库：https://github.com/wumingzhao1998/cuoti_shijuan
echo.
pause
