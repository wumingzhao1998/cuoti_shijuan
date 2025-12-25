# ⚠️ 重要提示：Vercel 不支持 Streamlit 应用

**Vercel 无法部署 Streamlit 应用！** Streamlit 需要长期运行的服务器进程，而 Vercel 是无服务器平台，只适合静态网站和 API 函数。

**请使用以下替代方案：**
- ✅ **Streamlit Cloud**（推荐，免费，官方支持）- 查看 `Streamlit_Cloud部署指南.md`
- ✅ **Railway**（备选）
- ✅ **Render**（备选）

---

# Vercel部署配置指南（已废弃）

## 环境变量配置

在Vercel部署时，需要在Vercel项目设置中配置以下环境变量。

### 访问环境变量配置

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择你的项目
3. 进入 **Settings** > **Environment Variables**

### 必需的环境变量

#### 1. 飞书应用配置（必需）

这些是访问飞书多维表格所必需的：

| 环境变量名 | 说明 | 示例值 |
|-----------|------|--------|
| `FEISHU_APP_ID` | 飞书应用的App ID | `cli_a9c84f993638dceb` |
| `FEISHU_APP_SECRET` | 飞书应用的App Secret | `vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i` |

**获取方式：**
- 访问 [飞书开放平台](https://open.feishu.cn/)
- 进入你的应用
- 在"凭证与基础信息"中查看App ID和App Secret

#### 2. 飞书多维表格配置（可选，有默认值）

如果使用默认的多维表格，可以不配置；如果需要使用其他表格，需要配置：

| 环境变量名 | 说明 | 默认值 | 是否必需 |
|-----------|------|--------|---------|
| `FEISHU_APP_TOKEN` | 多维表格的app_token | `NO9nbcpjraKeUCsSQkBcHL9gnhh` | 否 |
| `FEISHU_TABLE_ID` | 多维表格的table_id | `tblchSd315sqHTCt` | 否 |

**获取方式：**
- 在飞书多维表格中，点击右上角"..." > "复制链接"
- 从链接中提取 `app_token` 和 `table_id`

### 可选的环境变量

#### 3. 智谱AI配置（可选，用于生成类似题目功能）

如果不需要"生成类似题目"功能，可以不配置；如果需要，建议全部配置：

| 环境变量名 | 说明 | 推荐值 | 是否必需 |
|-----------|------|--------|---------|
| `LLM_API_KEY` | 智谱AI API Key | 你的API Key | 是（如果使用AI功能） |
| `LLM_API_BASE` | 智谱AI API Base URL | `https://open.bigmodel.cn/api/paas/v4` | 否（有默认值） |
| `LLM_MODEL` | 智谱AI模型名称 | `glm-4.6v` | 否（有默认值） |

**获取方式：**
- 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
- 注册/登录账号
- 在控制台创建API Key
- 确保API Key有权限使用 `glm-4.6v` 或 `glm-4` 模型

## 完整配置示例

### 最小配置（仅题库生成功能）

```
FEISHU_APP_ID=cli_a9c84f993638dceb
FEISHU_APP_SECRET=vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i
```

### 完整配置（包含AI生成功能）

```
FEISHU_APP_ID=cli_a9c84f993638dceb
FEISHU_APP_SECRET=vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i
FEISHU_APP_TOKEN=NO9nbcpjraKeUCsSQkBcHL9gnhh
FEISHU_TABLE_ID=tblchSd315sqHTCt
LLM_API_KEY=你的智谱AI_API_Key
LLM_API_BASE=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4.6v
```

## 在Vercel中配置步骤

### 方式一：通过Vercel Dashboard

1. 登录 [Vercel Dashboard](https://vercel.com/dashboard)
2. 选择你的项目：`cuoti_shijuan`
3. 点击 **Settings**
4. 在左侧菜单选择 **Environment Variables**
5. 点击 **Add New** 添加每个环境变量：
   - **Key**: 环境变量名（如 `FEISHU_APP_ID`）
   - **Value**: 环境变量值（如 `cli_a9c84f993638dceb`）
   - **Environment**: 选择适用的环境（Production、Preview、Development）
6. 点击 **Save**
7. 重复步骤5-6添加所有环境变量

### 方式二：通过Vercel CLI

```bash
# 安装Vercel CLI
npm i -g vercel

# 登录
vercel login

# 添加环境变量
vercel env add FEISHU_APP_ID
vercel env add FEISHU_APP_SECRET
vercel env add LLM_API_KEY

# 查看环境变量
vercel env ls
```

## 环境变量作用域

在Vercel中，可以为不同环境设置不同的值：

- **Production**: 生产环境（正式部署）
- **Preview**: 预览环境（Pull Request部署）
- **Development**: 开发环境（本地开发）

**建议：**
- 所有环境使用相同的配置
- 或者Production和Preview使用相同配置，Development可以留空

## 配置后操作

1. **重新部署**：配置环境变量后，需要重新部署项目才能生效
   - 在Vercel Dashboard中点击 **Deployments**
   - 点击最新的部署，选择 **Redeploy**

2. **验证配置**：
   - 访问部署后的应用
   - 检查是否能正常读取飞书数据
   - 如果配置了LLM_API_KEY，测试"生成类似题目"功能

## 安全注意事项

⚠️ **重要：**

1. **不要提交敏感信息到Git仓库**
   - `.feishu_config.json` 已在 `.gitignore` 中
   - 所有敏感信息都通过环境变量配置

2. **环境变量值保密**
   - 不要在代码中硬编码
   - 不要在公开的Issue或PR中暴露
   - 定期轮换API密钥

3. **Vercel环境变量权限**
   - 只有项目成员可以查看环境变量
   - 建议使用Vercel的团队功能管理权限

## 故障排查

### 问题1：无法读取飞书数据

**检查：**
- `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET` 是否正确配置
- 环境变量是否已重新部署生效
- 飞书应用权限是否正确配置

### 问题2：AI生成功能不工作

**检查：**
- `LLM_API_KEY` 是否正确配置
- API Key是否有效且有余额
- `LLM_API_BASE` 和 `LLM_MODEL` 是否正确（如果手动配置）

### 问题3：环境变量未生效

**解决方案：**
1. 确认环境变量已保存
2. 重新部署项目
3. 检查环境变量的作用域（Production/Preview/Development）

## 快速配置清单

- [ ] `FEISHU_APP_ID` - 飞书应用App ID
- [ ] `FEISHU_APP_SECRET` - 飞书应用App Secret
- [ ] `FEISHU_APP_TOKEN` - 多维表格app_token（可选，有默认值）
- [ ] `FEISHU_TABLE_ID` - 多维表格table_id（可选，有默认值）
- [ ] `LLM_API_KEY` - 智谱AI API Key（可选，用于AI功能）
- [ ] `LLM_API_BASE` - 智谱AI API Base URL（可选，有默认值）
- [ ] `LLM_MODEL` - 智谱AI模型名称（可选，有默认值）

## 参考链接

- [Vercel环境变量文档](https://vercel.com/docs/concepts/projects/environment-variables)
- [飞书开放平台](https://open.feishu.cn/)
- [智谱AI开放平台](https://open.bigmodel.cn/)
