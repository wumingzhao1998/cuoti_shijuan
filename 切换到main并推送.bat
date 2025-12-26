@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================
echo 切换到 main 分支并推送到 GitHub
echo ========================================
echo.

echo [1/5] 检查当前分支...
git branch --show-current
echo.

echo [2/5] 切换到 main 分支...
git checkout main
if errorlevel 1 (
    echo main 分支不存在，正在创建...
    git checkout -b main
)
echo ✓ 已切换到 main 分支
echo.

echo [3/5] 拉取远程 main 分支的更改...
git pull origin main --no-rebase
if errorlevel 1 (
    echo 警告：拉取可能失败，可能远程没有更改或网络问题
    echo 继续执行...
)
echo ✓ 拉取完成
echo.

echo [4/5] 合并 master 分支的更改（如果有）...
git merge master --no-edit 2>nul
if errorlevel 1 (
    echo 提示：master 分支可能没有需要合并的更改，这是正常的
)
echo ✓ 合并检查完成
echo.

echo [5/5] 添加所有更改...
git add .
echo ✓ 文件已添加
echo.

echo [6/6] 推送到 GitHub main 分支...
echo.
echo ⚠️ 如果提示输入用户名和密码：
echo - 用户名：你的 GitHub 用户名
echo - 密码：使用 Personal Access Token（不是 GitHub 密码）
echo.
pause

git push -u origin main
if errorlevel 1 (
    echo.
    echo 推送失败，可能原因：
    echo 1. 远程分支有本地没有的更改
    echo 2. 网络连接问题
    echo 3. GitHub 认证问题
    echo.
    echo 正在尝试强制合并推送...
    git pull origin main --rebase
    if errorlevel 1 (
        echo.
        echo 自动合并失败，请手动解决冲突后重试
        echo 或使用强制推送（谨慎使用）：git push -f origin main
        pause
        exit /b 1
    )
    echo.
    echo 重新尝试推送...
    git push -u origin main
    if errorlevel 1 (
        echo.
        echo 错误：推送仍然失败
        echo 请检查网络连接和 GitHub 认证
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo ✓ 完成！
echo ========================================
echo.
echo 代码已成功推送到 main 分支
echo Streamlit Cloud 会自动检测到更新并重新部署
echo.
pause
