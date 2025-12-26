# Streamlit Cloud 详细填写指南

## 📝 第一步：创建新应用

访问 https://share.streamlit.io/ 并登录后，点击 **"New app"** 按钮，会看到以下表单：

### 表单字段填写说明

#### 1. **Repository（仓库）**
- **填写内容**：`wumingzhao1998/cuoti_shijuan`
- **说明**：格式为 `用户名/仓库名`
- **如何获取**：
  - 从 GitHub 仓库地址提取
  - 例如：`https://github.com/wumingzhao1998/cuoti_shijuan` → 提取 `wumingzhao1998/cuoti_shijuan`
- **注意**：如果下拉列表中没有，说明需要先授权 Streamlit Cloud 访问你的 GitHub 仓库

#### 2. **Branch（分支）**
- **填写内容**：`main` 或 `master`
- **说明**：选择代码所在的分支
- **如何确认**：
  - 访问你的 GitHub 仓库
  - 查看默认分支名称（通常在仓库名称下方显示）
  - 如果显示 "main"，就填 `main`
  - 如果显示 "master"，就填 `master`

#### 3. **Main file path（主文件路径）**
- **填写内容**：`app.py`
- **说明**：你的 Streamlit 应用的主文件
- **注意**：
  - 如果 `app.py` 在仓库根目录，直接填 `app.py`
  - 如果在子目录，例如 `src/app.py`，则填 `src/app.py`
  - 本项目 `app.py` 在根目录，所以填 `app.py`

#### 4. **Advanced settings（高级设置，可选）**
- **Python version**：通常不需要修改，使用默认即可
- **其他设置**：首次部署不需要修改

### 完整填写示例

```
Repository:     wumingzhao1998/cuoti_shijuan
Branch:         main
Main file path: app.py
```

填写完成后，点击 **"Deploy!"** 按钮。

---

## 🔐 第二步：配置 Secrets（环境变量）

部署完成后，需要配置环境变量。点击应用右上角的 **"⋮"（三个点）** → **"Settings"** → **"Secrets"** 标签页。

### Secrets 配置格式

在文本框中粘贴以下内容（**完整复制，包括第一行的 `[secrets]`**）：

```toml
[secrets]
FEISHU_APP_ID = "cli_a9c84f993638dceb"
FEISHU_APP_SECRET = "vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i"
FEISHU_APP_TOKEN = "NO9nbcpjraKeUCsSQkBcHL9gnhh"
FEISHU_TABLE_ID = "tblchSd315sqHTCt"
LLM_API_KEY = "405fb47567834605a75e06dcc5b0e101.pxmImICNjiT3vWWv"
LLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
LLM_MODEL = "glm-4.6v"
```

### 各字段说明

| 字段名 | 说明 | 是否必需 | 示例值 |
|--------|------|---------|--------|
| `FEISHU_APP_ID` | 飞书应用的 App ID | ✅ 必需 | `cli_a9c84f993638dceb` |
| `FEISHU_APP_SECRET` | 飞书应用的 App Secret | ✅ 必需 | `vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i` |
| `FEISHU_APP_TOKEN` | 飞书多维表格的 app_token | ⚠️ 可选（有默认值） | `NO9nbcpjraKeUCsSQkBcHL9gnhh` |
| `FEISHU_TABLE_ID` | 飞书多维表格的 table_id | ⚠️ 可选（有默认值） | `tblchSd315sqHTCt` |
| `LLM_API_KEY` | 智谱AI的 API Key | ⚠️ 可选（用于AI功能） | `405fb47567834605a75e06dcc5b0e101.pxmImICNjiT3vWWv` |
| `LLM_API_BASE` | 智谱AI的 API Base URL | ⚠️ 可选（有默认值） | `https://open.bigmodel.cn/api/paas/v4` |
| `LLM_MODEL` | 智谱AI的模型名称 | ⚠️ 可选（有默认值） | `glm-4.6v` |

### 配置步骤

1. **打开 Secrets 页面**
   - 在应用页面，点击右上角 **"⋮"（三个点）**
   - 选择 **"Settings"**
   - 点击 **"Secrets"** 标签页

2. **粘贴配置**
   - 在文本框中粘贴上面的 TOML 配置
   - **重要**：必须包含第一行 `[secrets]`
   - 确保所有引号都是英文双引号 `"`

3. **保存**
   - 点击 **"Save"** 按钮
   - 应用会自动重新部署（通常需要 1-2 分钟）

4. **验证**
   - 等待部署完成
   - 刷新应用页面
   - 检查是否能正常读取飞书数据

---

## ✅ 第三步：验证部署

部署完成后，检查以下内容：

### 检查清单

- [ ] 应用可以正常访问（没有错误页面）
- [ ] 页面显示 "✓ 已检测到 FEISHU_APP_ID 和 FEISHU_APP_SECRET（来自 secrets.toml）"
- [ ] 能够选择学科和知识点
- [ ] 能够生成题库 WORD 文档
- [ ] 能够生成题库 HTML 文档
- [ ] 如果配置了 `LLM_API_KEY`，能够生成类似题目

### 常见问题

#### 问题1：显示 "请在下方输入 FEISHU_APP_ID..."
**原因**：Secrets 未正确配置或未保存

**解决方案**：
1. 检查 Secrets 配置是否正确
2. 确保点击了 "Save" 按钮
3. 等待应用重新部署完成
4. 刷新页面

#### 问题2：无法读取飞书数据 / `app secret invalid` 错误
**错误信息**：`RuntimeError: 获取 tenant_access_token 失败: {'code': 10014, 'msg': 'app secret invalid'}`

**原因**：`FEISHU_APP_SECRET` 无效或配置错误

**解决方案**：
1. **检查 Secrets 配置**
   - 进入 Streamlit Cloud → Settings → Secrets
   - 确认 `FEISHU_APP_SECRET` 的值是否正确
   - 检查是否有多余的空格、换行或引号问题

2. **验证飞书应用凭证**
   - 访问 [飞书开放平台](https://open.feishu.cn/)
   - 进入你的应用 → "凭证与基础信息"
   - 重新复制 `App ID` 和 `App Secret`
   - **注意**：App Secret 可能已重置，需要重新获取

3. **更新 Secrets 配置**
   - 在 Streamlit Cloud 的 Secrets 中更新正确的值
   - 确保格式正确：
     ```toml
     [secrets]
     FEISHU_APP_ID = "你的App_ID"
     FEISHU_APP_SECRET = "你的App_Secret"
     ```
   - 点击 "Save" 并等待重新部署

4. **检查 TOML 格式**
   - 确保使用英文双引号 `"`，不是中文引号 `"`
   - 确保值前后没有多余空格
   - 确保每行末尾没有多余字符

5. **查看日志**
   - 在 Streamlit Cloud → Settings → Logs 查看详细错误信息

#### 问题3：AI 生成功能不工作
**原因**：`LLM_API_KEY` 未配置或无效

**解决方案**：
1. 检查 Secrets 中是否包含 `LLM_API_KEY`
2. 验证 API Key 是否有效
3. 确认 API Key 有余额

---

## 📋 快速参考

### 最小配置（仅题库生成功能）

如果只需要生成题库，不需要 AI 功能，可以只配置：

```toml
[secrets]
FEISHU_APP_ID = "cli_a9c84f993638dceb"
FEISHU_APP_SECRET = "vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i"
```

### 完整配置（包含 AI 功能）

如果需要 AI 生成类似题目功能，使用完整配置：

```toml
[secrets]
FEISHU_APP_ID = "cli_a9c84f993638dceb"
FEISHU_APP_SECRET = "vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i"
FEISHU_APP_TOKEN = "NO9nbcpjraKeUCsSQkBcHL9gnhh"
FEISHU_TABLE_ID = "tblchSd315sqHTCt"
LLM_API_KEY = "405fb47567834605a75e06dcc5b0e101.pxmImICNjiT3vWWv"
LLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
LLM_MODEL = "glm-4.6v"
```

---

## 🎯 总结

**创建应用时填写：**
- Repository: `wumingzhao1998/cuoti_shijuan`
- Branch: `main`（或 `master`）
- Main file path: `app.py`

**配置 Secrets 时：**
- 直接复制上面的 TOML 配置
- 粘贴到 Secrets 文本框
- 点击 Save

**完成！** 🎉

