@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 推送最新代码更新到 GitHub
echo ========================================
echo.

echo [1/4] 添加所有更改...
git add .
if errorlevel 1 (
    echo 错误：添加文件失败
    pause
    exit /b 1
)
echo ✓ 文件已添加
echo.

echo [2/4] 提交更改...
git commit -m "修复 Streamlit Cloud 环境检测：改进 secrets 读取逻辑

- 改进 Streamlit Cloud 环境检测方法
- 修复手动输入界面在 Streamlit Cloud 上显示的问题
- 如果检测到 Streamlit Cloud，显示配置提示而不是输入框" --allow-empty
if errorlevel 1 (
    echo 警告：提交可能失败（没有更改或已提交）
)
echo ✓ 更改已提交
echo.

echo [3/4] 检查当前分支...
git branch --show-current
echo.

echo [4/4] 推送到 GitHub...
echo.
echo ⚠️ 如果提示输入用户名和密码：
echo - 用户名：你的 GitHub 用户名
echo - 密码：使用 Personal Access Token（不是 GitHub 密码）
echo.
pause

git push
if errorlevel 1 (
    echo.
    echo 推送失败，尝试推送到 origin...
    git push origin main 2>nul
    if errorlevel 1 (
        git push origin master 2>nul
        if errorlevel 1 (
            echo.
            echo 错误：推送失败
            echo 请检查网络连接和 GitHub 认证
            pause
            exit /b 1
        )
    )
)

echo.
echo ========================================
echo ✓ 推送完成！
echo ========================================
echo.
echo 代码已成功推送到 GitHub
echo Streamlit Cloud 会自动检测到更新并重新部署
echo.
pause
