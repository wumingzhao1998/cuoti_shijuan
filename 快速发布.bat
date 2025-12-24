@echo off
chcp 65001 >nul
title 快速发布到GitHub
cd /d "%~dp0"

echo 正在初始化Git仓库...
git init
git remote add origin https://github.com/wumingzhao1998/cuoti_shijuan.git 2>nul
git remote set-url origin https://github.com/wumingzhao1998/cuoti_shijuan.git 2>nul

echo 正在添加文件...
git add .

echo 正在提交...
git commit -m "发布 v1.0 版本"

echo 正在创建标签...
git tag -a v1.0 -m "版本 v1.0" -f

echo.
echo 准备推送到GitHub...
echo 请确保已配置GitHub认证
echo.
pause

echo 正在推送...
git push -u origin main 2>nul || git push -u origin master 2>nul || git branch -M main && git push -u origin main
git push origin v1.0

echo.
echo 完成！
pause
