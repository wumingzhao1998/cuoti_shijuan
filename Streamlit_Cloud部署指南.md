# Streamlit Cloud 部署指南

## 为什么 Vercel 不行？

Vercel 是无服务器平台，只适合部署静态网站和 API 函数。Streamlit 应用需要长期运行的服务器进程，因此无法在 Vercel 上正常运行。

## 推荐方案：Streamlit Cloud（免费）

Streamlit Cloud 是 Streamlit 官方提供的免费托管服务，最适合部署 Streamlit 应用。

### 部署步骤

#### 1. 准备 GitHub 仓库
确保你的代码已经推送到 GitHub：
- 仓库地址：`https://github.com/wumingzhao1998/cuoti_shijuan.git`
- 确保 `app.py` 和 `requirements.txt` 在仓库根目录

#### 2. 注册 Streamlit Cloud
1. 访问：https://share.streamlit.io/
2. 使用 GitHub 账号登录
3. 授权 Streamlit Cloud 访问你的 GitHub 仓库

#### 3. 部署应用
1. 点击 "New app"
2. 选择仓库：`wumingzhao1998/cuoti_shijuan`
3. 选择分支：`main` 或 `master`
4. 主文件路径：`app.py`
5. 点击 "Deploy!"

#### 4. 配置环境变量
在 Streamlit Cloud 的 App Settings 中，添加以下环境变量：

```
FEISHU_APP_ID=cli_a9c84f993638dceb
FEISHU_APP_SECRET=vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i
FEISHU_APP_TOKEN=NO9nbcpjraKeUCsSQkBcHL9gnhh
FEISHU_TABLE_ID=tblchSd315sqHTCt
LLM_API_KEY=405fb47567834605a75e06dcc5b0e101.pxmImICNjiT3vWWv
LLM_API_BASE=https://open.bigmodel.cn/api/paas/v4
LLM_MODEL=glm-4.6v
```

**配置步骤：**
1. 在 Streamlit Cloud 中打开你的应用
2. 点击右上角的 "⋮" (三个点)
3. 选择 "Settings"
4. 在 "Secrets" 标签页中，添加以下格式的配置：

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

5. 点击 "Save"
6. 应用会自动重新部署

### 优势
- ✅ 完全免费
- ✅ 专为 Streamlit 优化
- ✅ 自动部署（GitHub push 后自动更新）
- ✅ 支持环境变量/Secrets
- ✅ 提供公开 URL

---

## 备选方案：Railway

如果 Streamlit Cloud 不可用，可以使用 Railway：

### 部署步骤

1. 访问：https://railway.app/
2. 使用 GitHub 登录
3. 点击 "New Project" → "Deploy from GitHub repo"
4. 选择仓库：`wumingzhao1998/cuoti_shijuan`
5. 在 Settings 中配置环境变量（同上）
6. Railway 会自动检测 Python 项目并部署

### 注意事项
- Railway 免费额度有限，超出后需要付费
- 需要配置启动命令：`streamlit run app.py --server.port $PORT`

---

## 备选方案：Render

### 部署步骤

1. 访问：https://render.com/
2. 使用 GitHub 登录
3. 点击 "New" → "Web Service"
4. 选择仓库：`wumingzhao1998/cuoti_shijuan`
5. 配置：
   - **Name**: `cuoti-shijuan`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
6. 在 Environment 标签页添加环境变量（同上）

### 注意事项
- Render 免费版应用会在 15 分钟无活动后休眠
- 首次访问需要等待应用唤醒（约 30 秒）

---

## 总结

**推荐顺序：**
1. **Streamlit Cloud**（首选，最简单）
2. **Railway**（备选）
3. **Render**（备选，但会休眠）

**不推荐：**
- ❌ Vercel（不支持 Streamlit）
- ❌ Netlify（不支持 Streamlit）
