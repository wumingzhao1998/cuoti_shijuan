@echo off
chcp 65001 >nul
title 发布到GitHub - v1.0
cd /d "%~dp0"

echo ========================================
echo 飞书错题本生成试卷 - 发布到GitHub v1.0
echo ========================================
echo.

:: 检查是否已初始化git仓库
if not exist .git (
    echo [1/6] 初始化Git仓库...
    git init
    if errorlevel 1 (
        echo 错误：Git初始化失败
        pause
        exit /b 1
    )
    echo ✓ Git仓库初始化成功
) else (
    echo [1/6] Git仓库已存在
)
echo.

:: 检查是否已配置远程仓库
git remote get-url origin >nul 2>&1
if errorlevel 1 (
    echo [2/6] 配置远程仓库...
    echo 请输入GitHub仓库地址（例如：https://github.com/用户名/cuoti_shijuan.git）
    echo 或直接按回车使用默认地址：https://github.com/cuoti_shijuan/cuoti_shijuan.git
    set /p repo_url="仓库地址: "
    if "!repo_url!"=="" set repo_url=https://github.com/cuoti_shijuan/cuoti_shijuan.git
    git remote add origin !repo_url!
    if errorlevel 1 (
        echo 错误：添加远程仓库失败
        pause
        exit /b 1
    )
    echo ✓ 远程仓库配置成功
) else (
    echo [2/6] 远程仓库已配置
    git remote get-url origin
)
echo.

:: 创建.gitignore文件（如果不存在）
if not exist .gitignore (
    echo [3/6] 创建.gitignore文件...
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
    echo ✓ .gitignore文件已创建
) else (
    echo [3/6] .gitignore文件已存在
)
echo.

:: 添加所有文件
echo [4/6] 添加文件到Git...
git add .
if errorlevel 1 (
    echo 错误：添加文件失败
    pause
    exit /b 1
)
echo ✓ 文件已添加
echo.

:: 提交更改
echo [5/6] 提交更改...
git commit -m "发布 v1.0 版本

主要功能：
- 实现从飞书多维表格读取错题数据
- 支持多学科、多知识点选择
- 支持图片附件直接插入文档
- 生成 WORD 和 HTML 两种格式的题库文档
- 集成智谱AI GLM-4.6V大模型生成类似题目
- 支持多模态输入（图片+文本）
- 智能错误处理和用户提示
- 配置自动保存和管理"
if errorlevel 1 (
    echo 警告：提交失败（可能是没有更改）
)
echo ✓ 更改已提交
echo.

:: 创建v1.0标签
echo [6/6] 创建v1.0标签...
git tag -a v1.0 -m "版本 v1.0 - 初始发布版本" 2>nul
if errorlevel 1 (
    echo 警告：标签可能已存在，尝试删除后重新创建...
    git tag -d v1.0 2>nul
    git tag -a v1.0 -m "版本 v1.0 - 初始发布版本"
)
echo ✓ v1.0标签已创建
echo.

echo ========================================
echo 准备推送到GitHub...
echo ========================================
echo.
echo 请确认：
echo 1. 已配置GitHub认证（SSH密钥或Personal Access Token）
echo 2. 远程仓库地址正确
echo.
echo 按任意键继续推送到GitHub，或按Ctrl+C取消...
pause >nul
echo.

:: 推送到GitHub
echo 正在推送到GitHub...
git push -u origin main
if errorlevel 1 (
    echo.
    echo 尝试推送到master分支...
    git push -u origin master
    if errorlevel 1 (
        echo.
        echo 错误：推送失败
        echo.
        echo 可能的原因：
        echo 1. 未配置GitHub认证
        echo 2. 远程仓库不存在或没有权限
        echo 3. 分支名称不匹配（尝试手动推送）
        echo.
        echo 手动推送命令：
        echo   git push -u origin main
        echo   或
        echo   git push -u origin master
        pause
        exit /b 1
    )
)

echo.
echo 正在推送标签...
git push origin v1.0
if errorlevel 1 (
    echo 警告：标签推送失败，可以稍后手动推送
    echo 手动推送标签命令：git push origin v1.0
)

echo.
echo ========================================
echo ✓ 发布成功！
echo ========================================
echo.
echo 版本 v1.0 已推送到GitHub
echo 仓库地址：https://github.com/cuoti_shijuan/cuoti_shijuan
echo.
pause
