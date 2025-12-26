@echo off
chcp 65001 >nul
title 一键推送到GitHub
cd /d "%~dp0"

echo ========================================
echo 一键推送到GitHub - v1.0
echo ========================================
echo.
echo 目标仓库：https://github.com/wumingzhao1998/cuoti_shijuan.git
echo.

:: 初始化Git仓库
if not exist .git (
    echo [1/7] 初始化Git仓库...
    git init
    echo ✓ 已初始化
) else (
    echo [1/7] ✓ Git仓库已存在
)
echo.

:: 配置远程仓库
echo [2/7] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/wumingzhao1998/cuoti_shijuan.git
echo ✓ 远程仓库已配置
echo.

:: 确保有main分支
echo [3/7] 检查分支...
git checkout -b main 2>nul || git checkout main 2>nul || git branch -M main 2>nul
echo ✓ 分支已就绪
echo.

:: 添加文件
echo [4/7] 添加文件...
git add .
echo ✓ 文件已添加
echo.

:: 提交
echo [5/7] 提交更改...
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
echo ✓ 已提交
echo.

:: 创建标签
echo [6/7] 创建v1.0标签...
git tag -d v1.0 2>nul
git tag -a v1.0 -m "版本 v1.0 - 初始发布版本"
echo ✓ 标签已创建
echo.

:: 推送
echo [7/7] 推送到GitHub...
echo.
echo ⚠️ 重要提示：
echo 推送时需要GitHub认证，请选择以下方式之一：
echo.
echo 方式1：使用Personal Access Token（推荐）
echo   - 访问：https://github.com/settings/tokens
echo   - 生成新token（勾选repo权限）
echo   - 推送时，用户名输入GitHub用户名，密码输入token
echo.
echo 方式2：使用SSH密钥
echo   - 确保已配置SSH密钥
echo   - 运行：git remote set-url origin git@github.com:wumingzhao1998/cuoti_shijuan.git
echo.
echo 按任意键继续推送...
pause >nul
echo.

echo 正在推送代码到main分支...
git push -u origin main
if errorlevel 1 (
    echo.
    echo ⚠️ 推送失败，可能的原因：
    echo 1. 未配置GitHub认证
    echo 2. 远程仓库不存在或没有权限
    echo 3. 网络连接问题
    echo.
    echo 请检查：
    echo - 确保GitHub上已创建仓库：https://github.com/wumingzhao1998/cuoti_shijuan
    echo - 确保已配置认证（Personal Access Token或SSH密钥）
    echo - 检查网络连接
    echo.
    pause
    exit /b 1
)

echo.
echo 正在推送标签...
git push origin v1.0
if errorlevel 1 (
    echo ⚠️ 标签推送失败，可以稍后手动推送：git push origin v1.0
) else (
    echo ✓ 标签推送成功
)

echo.
echo ========================================
echo ✓ 推送完成！
echo ========================================
echo.
echo 版本 v1.0 已成功推送到GitHub
echo 仓库地址：https://github.com/wumingzhao1998/cuoti_shijuan
echo 标签地址：https://github.com/wumingzhao1998/cuoti_shijuan/releases/tag/v1.0
echo.
pause

