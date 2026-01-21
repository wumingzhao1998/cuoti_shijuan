@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo === 创建性能优化分支 ===
echo.

echo [1/3] 添加并提交当前更改...
git add -A
git commit -m "修复合并冲突"

echo.
echo [2/3] 创建新分支 performance-optimization...
git checkout -b performance-optimization

echo.
echo [3/3] 完成！
git branch

pause
