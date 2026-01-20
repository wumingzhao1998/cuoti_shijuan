@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === 推送修复到 GitHub ===
echo.

echo [1/4] 添加更改...
git add -A

echo.
echo [2/4] 提交...
git commit -m "优化界面：移除主页配置状态显示"

echo.
echo [3/4] 推送到 review-q...
git push origin review-q

echo.
echo [4/4] 合并到 main 并推送...
git checkout main
git pull origin main
git merge review-q -m "合并修复"
git push origin main
git checkout review-q

echo.
echo 完成！请等待 Streamlit Cloud 重新部署（约2-3分钟）
pause
