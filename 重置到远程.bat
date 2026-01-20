@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === 完全重置到远程 origin/review-q 分支 ===
echo.
echo 警告：这将丢弃所有本地修改！
echo.

git fetch origin
git reset --hard origin/review-q

echo.
echo === 重置完成，当前文件列表 ===
dir /b

echo.
echo 完成！
pause
