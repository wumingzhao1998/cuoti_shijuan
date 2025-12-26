@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 推送代码更新到 GitHub
echo ========================================
echo.

echo [1/4] 添加文件...
git add .
if errorlevel 1 (
    echo 错误：添加文件失败
    pause
    exit /b 1
)
echo ✓ 文件已添加
echo.

echo [2/4] 提交更改...
git commit -m "优化 Streamlit Cloud 部署：禁用手动输入，自动读取 Secrets

- 改进 safe_get_secret 函数，支持多种方式读取 secrets
- 在 Streamlit Cloud 上禁用手动输入界面
- 如果配置缺失，显示清晰的配置提示
- 优化环境检测逻辑" --allow-empty
if errorlevel 1 (
    echo 警告：提交可能失败（没有更改或已提交）
)
echo ✓ 更改已提交
echo.

echo [3/4] 检查远程仓库...
git remote -v >nul 2>&1
if errorlevel 1 (
    echo 添加远程仓库...
    git remote add origin https://github.com/wumingzhao1998/cuoti_shijuan.git
)
echo ✓ 远程仓库已配置
echo.

echo [4/4] 推送到 GitHub...
echo.
echo ⚠️ 如果提示输入用户名和密码：
echo - 用户名：你的 GitHub 用户名
echo - 密码：使用 Personal Access Token（不是 GitHub 密码）
echo.
echo 如果还没有 Token，访问：https://github.com/settings/tokens
echo.
pause

git push -u origin main
if errorlevel 1 (
    echo.
    echo 尝试推送到 master 分支...
    git push -u origin master
    if errorlevel 1 (
        echo.
        echo 错误：推送失败
        echo 请检查网络连接和 GitHub 认证
        pause
        exit /b 1
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
