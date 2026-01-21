@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === 强制推送到 GitHub ===
echo.

echo [1/6] 查看当前状态...
git status

echo.
echo [2/6] 添加所有更改...
git add -A

echo.
echo [3/6] 提交更改...
git commit -m "性能优化：预生成类似题、缓存机制、每日练习限制"

echo.
echo [4/6] 强制推送到 review-q...
git push origin review-q --force

echo.
echo [5/6] 切换到 main 并合并...
git checkout main
git pull origin main
git merge review-q -m "合并优化" --no-edit
git push origin main --force

echo.
echo [6/6] 切换回 review-q...
git checkout review-q

echo.
echo === 完成！请等待 Streamlit Cloud 重新部署 ===
pause
