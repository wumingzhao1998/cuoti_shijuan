# GitHub发布指南 - v1.0

## 快速发布步骤

### 方式一：使用批处理脚本（推荐）

直接双击运行 `发布到GitHub.bat` 文件，脚本会自动完成所有步骤。

### 方式二：手动执行命令

如果脚本无法运行，可以按照以下步骤手动执行：

#### 1. 打开命令提示符（CMD）或PowerShell

在项目目录下打开终端。

#### 2. 初始化Git仓库（如果还没有）

```bash
git init
```

#### 3. 配置远程仓库

```bash
git remote add origin https://github.com/cuoti_shijuan/cuoti_shijuan.git
```

如果远程仓库已存在，可以更新：
```bash
git remote set-url origin https://github.com/cuoti_shijuan/cuoti_shijuan.git
```

#### 4. 创建.gitignore文件（如果还没有）

确保 `.gitignore` 文件包含以下内容（脚本会自动创建）：

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
ENV/
.venv

# 配置文件（包含敏感信息）
.feishu_config.json

# 打包文件
dist/
build/
*.spec

# IDE
.vscode/
.idea/
*.swp
*.swo

# 系统文件
.DS_Store
Thumbs.db
```

#### 5. 添加所有文件

```bash
git add .
```

#### 6. 提交更改

```bash
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
```

#### 7. 创建v1.0标签

```bash
git tag -a v1.0 -m "版本 v1.0 - 初始发布版本"
```

#### 8. 推送到GitHub

首先推送代码：
```bash
git push -u origin main
```

如果main分支不存在，尝试：
```bash
git push -u origin master
```

然后推送标签：
```bash
git push origin v1.0
```

## 注意事项

### 1. GitHub认证配置

确保已配置GitHub认证，可以使用以下方式之一：

**方式A：使用SSH密钥（推荐）**
```bash
# 检查是否已有SSH密钥
ls ~/.ssh

# 如果没有，生成新的SSH密钥
ssh-keygen -t ed25519 -C "your_email@example.com"

# 将公钥添加到GitHub账户
cat ~/.ssh/id_ed25519.pub
# 复制输出内容，在GitHub Settings > SSH and GPG keys 中添加
```

**方式B：使用Personal Access Token**
1. 访问 GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)
2. 生成新token，勾选 `repo` 权限
3. 推送时使用token作为密码

### 2. 仓库创建

如果GitHub上还没有 `cuoti_shijuan` 仓库，需要先创建：
1. 访问 https://github.com/new
2. 仓库名称：`cuoti_shijuan`
3. 选择 Public 或 Private
4. 不要初始化README、.gitignore或license（因为本地已有）

### 3. 分支名称

如果推送时提示分支不存在，可以：
- 使用 `git push -u origin main`（GitHub默认分支）
- 或使用 `git push -u origin master`（旧版Git默认分支）
- 或先创建分支：`git branch -M main`

## 验证发布

发布成功后，访问以下地址验证：
- 仓库地址：https://github.com/cuoti_shijuan/cuoti_shijuan
- 标签地址：https://github.com/cuoti_shijuan/cuoti_shijuan/releases/tag/v1.0

## 常见问题

### Q: 推送时提示认证失败
**A:** 检查GitHub认证配置，确保SSH密钥或Personal Access Token正确设置。

### Q: 提示远程仓库已存在
**A:** 使用 `git remote set-url origin <url>` 更新远程仓库地址。

### Q: 提示分支不存在
**A:** 先创建分支：`git branch -M main`，然后再推送。

### Q: 标签推送失败
**A:** 可以稍后单独推送标签：`git push origin v1.0`

## 后续更新

发布v1.0后，后续更新可以使用：

```bash
# 添加更改
git add .

# 提交
git commit -m "更新说明"

# 推送
git push origin main
```

创建新版本标签：
```bash
git tag -a v1.1 -m "版本 v1.1 - 更新说明"
git push origin v1.1
```
