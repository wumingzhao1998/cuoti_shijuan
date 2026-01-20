@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo  推送代码到 Streamlit Cloud
echo ========================================
echo.

echo [1/4] 检查 Git 状态...
git status
echo.

echo [2/4] 添加所有更改...
git add -A
echo.

echo [3/4] 提交更改...
git commit -m "重构界面：简化主页为两个按钮，添加进度条，优化用户体验"
echo.

echo [4/4] 推送到远程仓库...
git push
echo.

echo ========================================
echo  推送完成！
echo  Streamlit Cloud 会自动检测到更改并重新部署
echo  请等待 2-5 分钟后刷新您的应用
echo ========================================
echo.
pause
