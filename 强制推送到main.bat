@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo ⚠️ 强制推送到 main 分支（谨慎使用）
echo ========================================
echo.
echo 警告：此操作会用本地代码覆盖远程代码
echo 仅在确定远程代码不重要时使用
echo.
echo 按任意键继续，或按 Ctrl+C 取消...
pause >nul
echo.

echo 切换到 main 分支...
git checkout main 2>nul || git checkout -b main
echo.

echo 合并 master 分支...
git merge master --no-edit 2>nul
echo.

echo 添加所有更改...
git add .
echo.

echo 强制推送到 main 分支...
echo ⚠️ 如果提示输入用户名和密码：
echo - 用户名：你的 GitHub 用户名
echo - 密码：使用 Personal Access Token
echo.
pause

git push -f origin main
if errorlevel 1 (
    echo.
    echo 推送失败，请检查网络连接和 GitHub 认证
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 强制推送完成！
echo ========================================
echo.
echo 代码已强制推送到 main 分支
echo Streamlit Cloud 会自动检测到更新并重新部署
echo.
pause
