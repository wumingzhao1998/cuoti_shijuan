@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo  合并到 main 分支并推送到 Streamlit Cloud
echo ========================================
echo.

echo [1/6] 检查当前分支...
git branch
echo.

echo [2/6] 添加并提交当前分支的更改...
git add -A
git commit -m "重构界面：简化主页为两个按钮，添加进度条，优化用户体验"
echo.

echo [3/6] 切换到 main 分支...
git checkout main
echo.

echo [4/6] 合并 review-q 分支到 main...
git merge review-q -m "合并 review-q: 界面重构和功能优化"
echo.

echo [5/6] 推送 main 分支到远程仓库...
git push origin main
echo.

echo [6/6] 切换回 review-q 分支...
git checkout review-q
echo.

echo ========================================
echo  推送完成！
echo  已将 review-q 合并到 main 并推送
echo  Streamlit Cloud 会自动检测到更改并重新部署
echo  请等待 2-5 分钟后刷新您的应用
echo ========================================
echo.
pause
