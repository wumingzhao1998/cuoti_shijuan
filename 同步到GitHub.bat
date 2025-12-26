@echo off
chcp 65001 >nul
title 同步项目到GitHub
cd /d "%~dp0"

echo ========================================
echo 同步项目到GitHub
echo ========================================
echo.
echo 目标仓库：https://github.com/wumingzhao1998/cuoti_shijuan.git
echo.

:: 步骤1：初始化Git仓库
echo [1/8] 初始化Git仓库...
if not exist .git (
    git init
    if errorlevel 1 (
        echo 错误：Git初始化失败
        pause
        exit /b 1
    )
    echo ✓ Git仓库已初始化
) else (
    echo ✓ Git仓库已存在
)
echo.

:: 步骤2：配置远程仓库
echo [2/8] 配置远程仓库...
git remote remove origin >nul 2>&1
git remote add origin https://github.com/wumingzhao1998/cuoti_shijuan.git
if errorlevel 1 (
    echo 错误：配置远程仓库失败
    pause
    exit /b 1
)
echo ✓ 远程仓库已配置
echo.

:: 步骤3：确保.gitignore存在
echo [3/8] 检查.gitignore文件...
if not exist .gitignore (
    echo 创建.gitignore文件...
    (
        echo # Python
        echo __pycache__/
        echo *.py[cod]
        echo *$py.class
        echo *.so
        echo .Python
        echo env/
        echo venv/
        echo ENV/
        echo .venv
        echo.
        echo # 配置文件（包含敏感信息）
        echo .feishu_config.json
        echo.
        echo # 打包文件
        echo dist/
        echo build/
        echo *.spec
        echo.
        echo # IDE
        echo .vscode/
        echo .idea/
        echo *.swp
        echo *.swo
        echo.
        echo # 系统文件
        echo .DS_Store
        echo Thumbs.db
    ) > .gitignore
    echo ✓ .gitignore已创建
) else (
    echo ✓ .gitignore已存在
)
echo.

:: 步骤4：创建main分支
echo [4/8] 创建/切换到main分支...
git checkout -b main >nul 2>&1
if errorlevel 1 (
    git checkout main >nul 2>&1
    if errorlevel 1 (
        git branch -M main >nul 2>&1
    )
)
echo ✓ 分支已就绪
echo.

:: 步骤5：添加所有文件
echo [5/8] 添加所有文件到Git...
git add .
if errorlevel 1 (
    echo 错误：添加文件失败
    pause
    exit /b 1
)
echo ✓ 文件已添加
echo.

:: 步骤6：提交更改
echo [6/8] 提交更改...
git commit -m "发布 v1.0 版本

主要功能：
- 实现从飞书多维表格读取错题数据
- 支持多学科、多知识点选择
- 支持图片附件直接插入文档
- 生成 WORD 和 HTML 两种格式的题库文档
- 集成智谱AI GLM-4.6V大模型生成类似题目
- 支持多模态输入（图片+文本）
- 智能错误处理和用户提示
- 配置自动保存和管理" --allow-empty
if errorlevel 1 (
    echo 警告：提交可能失败（可能是没有更改）
)
echo ✓ 已提交
echo.

:: 步骤7：创建v1.0标签
echo [7/8] 创建v1.0标签...
git tag -d v1.0 >nul 2>&1
git tag -a v1.0 -m "版本 v1.0 - 初始发布版本" >nul 2>&1
if errorlevel 1 (
    git tag -a v1.0 -m "版本 v1.0 - 初始发布版本"
)
echo ✓ 标签已创建
echo.

:: 步骤8：推送到GitHub
echo [8/8] 推送到GitHub...
echo.
echo ⚠️ 重要提示：
echo 推送时需要GitHub认证信息
echo.
echo 如果使用HTTPS方式：
echo - 用户名：输入 wumingzhao1998
echo - 密码：输入 Personal Access Token（不是GitHub密码）
echo.
echo 如果还没有Token：
echo 1. 访问：https://github.com/settings/tokens
echo 2. 点击 "Generate new token (classic)"
echo 3. 勾选 repo 权限
echo 4. 生成并复制token
echo 5. 推送时使用token作为密码
echo.
echo 按任意键开始推送...
pause >nul
echo.

echo 正在推送代码到main分支...
git push -u origin main
if errorlevel 1 (
    echo.
    echo ========================================
    echo 推送失败
    echo ========================================
    echo.
    echo 可能的原因：
    echo 1. 未配置GitHub认证（需要Personal Access Token）
    echo 2. 远程仓库不存在或没有权限
    echo 3. 网络连接问题
    echo.
    echo 解决方案：
    echo 1. 确保GitHub上已创建仓库：https://github.com/wumingzhao1998/cuoti_shijuan
    echo 2. 生成Personal Access Token：https://github.com/settings/tokens
    echo 3. 重新运行此脚本，推送时使用token作为密码
    echo.
    echo 或者手动执行：
    echo   git push -u origin main
    echo.
    pause
    exit /b 1
)

echo.
echo 正在推送v1.0标签...
git push origin v1.0
if errorlevel 1 (
    echo 警告：标签推送失败，可以稍后手动推送
    echo 命令：git push origin v1.0
) else (
    echo ✓ 标签推送成功
)

echo.
echo ========================================
echo ✓ 同步完成！
echo ========================================
echo.
echo 项目已成功同步到GitHub
echo 仓库地址：https://github.com/wumingzhao1998/cuoti_shijuan
echo 标签地址：https://github.com/wumingzhao1998/cuoti_shijuan/releases/tag/v1.0
echo.
echo 可以访问上述地址查看项目
echo.
pause

