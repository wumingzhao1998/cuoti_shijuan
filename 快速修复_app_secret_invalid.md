# 快速修复：app secret invalid 错误

## ❌ 错误信息
```
RuntimeError: 获取 tenant_access_token 失败: {'code': 10014, 'msg': 'app secret invalid'}
```

## 🔧 解决步骤（3步）

### 步骤1：获取最新的飞书 App Secret

1. **访问飞书开放平台**
   - 打开：https://open.feishu.cn/
   - 登录你的账号

2. **找到你的应用**
   - 点击左侧 "应用管理"
   - 找到应用（App ID: `cli_a9c84f993638dceb`）

3. **查看 App Secret**
   - 点击应用进入详情页
   - 选择 "凭证与基础信息" 标签页
   - 找到 **App Secret** 字段
   - **如果显示 `****`**：说明已隐藏，需要点击 "重置" 获取新密钥
   - **如果有显示值**：直接复制（确保完整复制，不要遗漏字符）

4. **重要提示**
   - ⚠️ 如果之前重置过 App Secret，旧的 Secret 会失效
   - ⚠️ 新 Secret 只显示一次，请立即复制保存
   - ⚠️ App Secret 应该是类似 `vEa2dJyfpd0D0fDwEsBW6eoPTn3nKj3i` 这样的字符串

---

### 步骤2：更新 Streamlit Cloud Secrets

1. **打开 Streamlit Cloud**
   - 访问你的应用页面
   - 点击右上角 **"⋮"（三个点）**
   - 选择 **"Settings"**

2. **进入 Secrets 配置**
   - 点击 **"Secrets"** 标签页
   - 你会看到一个文本框

3. **更新配置**
   - 删除文本框中的全部内容
   - 粘贴以下内容，**并用从飞书平台获取的最新 App Secret 替换 `你的最新App_Secret`**：

   ```toml
   [secrets]
   FEISHU_APP_ID = "cli_a9c84f993638dceb"
   FEISHU_APP_SECRET = "你的最新App_Secret"
   FEISHU_APP_TOKEN = "NO9nbcpjraKeUCsSQkBcHL9gnhh"
   FEISHU_TABLE_ID = "tblchSd315sqHTCt"
   LLM_API_KEY = "405fb47567834605a75e06dcc5b0e101.pxmImICNjiT3vWWv"
   LLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
   LLM_MODEL = "glm-4.6v"
   ```

4. **检查格式**（非常重要！）
   - ✅ 第一行必须是 `[secrets]`（不要删除）
   - ✅ 使用英文双引号 `"`，不是中文引号 `"` 或 `"`
   - ✅ App Secret 值前后不要有空格
   - ✅ 每行末尾不要有多余字符
   - ✅ 确保没有遗漏任何字符

5. **保存**
   - 点击 **"Save"** 按钮
   - 等待 1-2 分钟让应用重新部署

---

### 步骤3：验证修复

1. **等待部署完成**
   - 刷新应用页面
   - 查看右上角是否有 "正在重新部署" 的提示

2. **检查是否修复**
   - ✅ 不再显示错误信息
   - ✅ 显示 "✓ 已检测到 FEISHU_APP_ID 和 FEISHU_APP_SECRET（来自 secrets.toml）"
   - ✅ 能够正常选择学科和知识点
   - ✅ 能够正常读取飞书数据

---

## 🆘 如果仍然失败

### 检查清单

- [ ] App Secret 是否从飞书平台最新获取？
- [ ] Secrets 配置中是否使用了英文双引号 `"`？
- [ ] App Secret 值前后是否有空格？
- [ ] 是否点击了 "Save" 按钮？
- [ ] 是否等待了足够的时间让应用重新部署？

### 查看详细日志

1. 在 Streamlit Cloud 应用页面
2. 点击右上角 "⋮" → "Settings" → "Logs"
3. 查看最新的错误信息
4. 如果错误仍然存在，复制完整的错误信息

### 本地测试验证

如果本地可以正常工作，说明 App Secret 本身是正确的：

1. **检查本地配置**
   - 查看 `.feishu_config.json` 文件
   - 确认 `FEISHU_APP_SECRET` 的值

2. **本地运行测试**
   - 运行 `streamlit run app.py`
   - 如果能正常工作，说明 App Secret 有效
   - 然后将相同的值复制到 Streamlit Cloud Secrets

---

## 📝 完整配置示例

假设你从飞书平台获取的最新 App Secret 是 `新密钥123456`，那么 Secrets 配置应该是：

```toml
[secrets]
FEISHU_APP_ID = "cli_a9c84f993638dceb"
FEISHU_APP_SECRET = "新密钥123456"
FEISHU_APP_TOKEN = "NO9nbcpjraKeUCsSQkBcHL9gnhh"
FEISHU_TABLE_ID = "tblchSd315sqHTCt"
LLM_API_KEY = "405fb47567834605a75e06dcc5b0e101.pxmImICNjiT3vWWv"
LLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
LLM_MODEL = "glm-4.6v"
```

**注意**：请将 `新密钥123456` 替换为你实际获取的 App Secret！

---

**最后更新**：2025-12-18
