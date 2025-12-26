@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 修复 Secrets 读取并推送
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
git commit -m "改进 Secrets 读取和错误提示

- 简化 safe_get_secret 函数，使用标准 st.secrets.get() 方法
- 改进错误提示，提供更详细的配置步骤和排查建议
- 添加更明确的重新部署提示" --allow-empty
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
echo.
echo 下一步操作：
echo 1. Streamlit Cloud 会自动检测到更新并重新部署
echo 2. 同时，请在 Secrets 页面添加一个空行并点击 Save 以触发重新部署
echo 3. 等待 3-5 分钟让应用重新部署
echo 4. 刷新应用页面查看是否已修复
echo.
pause
