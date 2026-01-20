@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === 合并 review-q 分支到 main ===
echo.

echo [1/5] 当前分支状态...
git branch
git status --short

echo.
echo [2/5] 切换到 main 分支...
git checkout main

echo.
echo [3/5] 拉取最新 main...
git pull origin main

echo.
echo [4/5] 合并 review-q 到 main...
git merge review-q -m "合并 review-q 分支"

echo.
echo [5/5] 推送到远程...
git push origin main

echo.
echo === 完成！切换回 review-q ===
git checkout review-q

echo.
echo 合并完成！
pause
