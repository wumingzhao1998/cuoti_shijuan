# Streamlit Cloud 错误排查指南

## ❌ 错误：`app secret invalid`

### 错误信息
```
RuntimeError: 获取 tenant_access_token 失败: {'code': 10014, 'msg': 'app secret invalid'}
```

### 问题原因
`FEISHU_APP_SECRET`（飞书应用密钥）无效或配置错误。

### 解决步骤

#### 步骤1：验证飞书应用凭证

1. **访问飞书开放平台**
   - 打开：https://open.feishu.cn/
   - 使用你的飞书账号登录

2. **进入应用管理**
   - 点击左侧菜单 "应用管理"
   - 找到你的应用（App ID: `cli_a9c84f993638dceb`）

3. **查看凭证信息**
   - 点击应用进入详情页
   - 选择 "凭证与基础信息" 标签页
   - 查看并复制：
     - **App ID**：`cli_a9c84f993638dceb`
     - **App Secret**：点击 "显示" 或 "重置" 获取最新密钥

4. **重要提示**
   - 如果 App Secret 显示为 `****`，说明已隐藏
   - 如果之前重置过，旧的 Secret 会失效
   - 需要重新复制或重置获取新的 Secret

#### 步骤2：更新 Streamlit Cloud Secrets

1. **打开 Secrets 配置**
   - 在 Streamlit Cloud 应用页面
   - 点击右上角 "⋮" → "Settings" → "Secrets"

2. **更新配置**
   - 删除旧的 `FEISHU_APP_SECRET` 值
   - 粘贴从飞书开放平台获取的最新 `App Secret`
   - 确保格式正确：

   ```toml
   [secrets]
   FEISHU_APP_ID = "cli_a9c84f993638dceb"
   FEISHU_APP_SECRET = "从飞书平台获取的最新密钥"
   ```

3. **检查格式**
   - ✅ 使用英文双引号 `"`，不是中文引号 `"`
   - ✅ 值前后没有多余空格
   - ✅ 每行末尾没有多余字符
   - ✅ 第一行必须是 `[secrets]`

4. **保存并等待**
   - 点击 "Save" 按钮
   - 等待应用自动重新部署（1-2 分钟）
   - 刷新应用页面验证

#### 步骤3：验证修复

部署完成后，检查：
- [ ] 应用页面不再显示错误
- [ ] 显示 "✓ 已检测到 FEISHU_APP_ID 和 FEISHU_APP_SECRET（来自 secrets.toml）"
- [ ] 能够正常选择学科和知识点
- [ ] 能够正常读取飞书数据

---

## ❌ 其他常见错误

### 错误1：`FEISHU_APP_ID` 或 `FEISHU_APP_SECRET` 未找到

**错误信息**：页面显示 "请在下方输入 FEISHU_APP_ID..."

**原因**：Secrets 未正确配置

**解决方案**：
1. 检查 Secrets 中是否包含 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`
2. 确保第一行是 `[secrets]`
3. 确保点击了 "Save" 按钮
4. 等待重新部署完成

### 错误2：`LLM_API_KEY` 无效

**错误信息**：`API错误 401: 令牌已过期或验证不正确`

**原因**：智谱AI API Key 无效或已过期

**解决方案**：
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 检查 API Key 是否有效
3. 检查 API Key 是否有余额
4. 如有必要，重新生成 API Key 并更新 Secrets

### 错误3：无法读取飞书多维表格数据

**错误信息**：`无法获取记录` 或 `权限不足`

**原因**：飞书应用权限配置不正确

**解决方案**：
1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 进入应用 → "权限管理"
3. 确保已添加以下权限：
   - `bitable:app` - 查看多维表格应用
   - `bitable:app:readonly` - 查看多维表格数据
4. 保存权限配置
5. 如有必要，重新发布应用版本

---

## 🔍 调试技巧

### 查看 Streamlit Cloud 日志

1. **访问日志**
   - 在应用页面，点击右上角 "⋮" → "Settings"
   - 选择 "Logs" 标签页
   - 查看详细的错误信息和堆栈跟踪

2. **常见日志位置**
   - 部署日志：显示构建和启动过程
   - 运行时日志：显示应用运行时的错误

### 本地测试

在更新 Streamlit Cloud 配置前，可以在本地测试：

1. **创建本地 secrets.toml**
   - 在项目根目录创建 `.streamlit/secrets.toml`
   - 内容格式：
     ```toml
     [secrets]
     FEISHU_APP_ID = "你的App_ID"
     FEISHU_APP_SECRET = "你的App_Secret"
     ```

2. **本地运行测试**
   - 运行 `streamlit run app.py`
   - 验证是否能正常读取飞书数据
   - 如果本地正常，说明配置正确，问题可能在 Streamlit Cloud

---

## 📞 获取帮助

如果以上步骤都无法解决问题：

1. **检查飞书应用状态**
   - 确认应用是否已发布
   - 确认应用是否已关联多维表格

2. **检查网络连接**
   - Streamlit Cloud 需要能够访问飞书 API
   - 某些地区可能需要代理

3. **查看完整错误日志**
   - 在 Streamlit Cloud → Settings → Logs
   - 复制完整的错误信息
   - 根据具体错误信息进一步排查

---

**最后更新**：2025-12-18

