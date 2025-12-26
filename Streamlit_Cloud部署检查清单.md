# Streamlit Cloud 部署检查清单

## ✅ 代码兼容性检查

### 1. 依赖检查
- ✅ `streamlit` - 已包含
- ✅ `requests` - 已包含
- ✅ `python-docx` - 已包含
- ✅ 所有依赖都在 `requirements.txt` 中

### 2. 配置读取优先级（已优化）
代码按以下优先级读取配置：
1. **环境变量** (`os.getenv()`) - ✅ Streamlit Cloud 支持
2. **st.secrets** - ✅ Streamlit Cloud 推荐方式
3. **本地配置文件** (`.feishu_config.json`) - ⚠️ 在 Streamlit Cloud 上可能不可写
4. **Session State** - ✅ 临时存储，适合运行时配置

**结论：** ✅ 代码已优化，优先使用环境变量和 `st.secrets`，在 Streamlit Cloud 上可以正常工作。

### 3. 文件系统操作
- ✅ 配置文件写入已添加异常处理，在只读文件系统上会静默失败
- ✅ 所有文件操作都有 try-except 保护
- ✅ 不依赖本地文件系统持久化（优先使用环境变量/Secrets）

### 4. 网络请求
- ✅ 使用 `requests` 库进行 HTTP 请求
- ✅ 所有 API 调用都有超时设置
- ✅ 错误处理完善

## 📋 部署前检查清单

### 代码准备
- [x] `app.py` 在仓库根目录
- [x] `requirements.txt` 包含所有依赖
- [x] 代码已推送到 GitHub
- [x] 代码已测试通过（本地运行正常）

### GitHub 仓库
- [ ] 仓库地址：`https://github.com/wumingzhao1998/cuoti_shijuan.git`
- [ ] 主分支：`main` 或 `master`
- [ ] 所有文件已提交并推送

### Streamlit Cloud 配置
- [ ] 已注册 Streamlit Cloud 账号
- [ ] 已授权 GitHub 访问
- [ ] 已创建新应用
- [ ] 已选择正确的仓库和分支
- [ ] 主文件路径设置为：`app.py`

### 环境变量配置（Streamlit Cloud Secrets）
在 Streamlit Cloud 的 **Settings → Secrets** 中配置：

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

## 🚀 部署步骤

1. **访问 Streamlit Cloud**
   - 打开：https://share.streamlit.io/
   - 使用 GitHub 账号登录

2. **创建新应用**
   - 点击 "New app"
   - Repository: `wumingzhao1998/cuoti_shijuan`
   - Branch: `main` 或 `master`
   - Main file path: `app.py`
   - 点击 "Deploy!"

3. **配置 Secrets**
   - 部署完成后，点击右上角 "⋮" → "Settings"
   - 进入 "Secrets" 标签页
   - 粘贴上面的 TOML 配置
   - 点击 "Save"
   - 应用会自动重新部署

4. **验证部署**
   - 等待部署完成（通常 1-2 分钟）
   - 访问应用 URL
   - 检查是否能正常读取飞书数据
   - 测试生成题库功能
   - 测试生成类似题目功能（如果配置了 LLM_API_KEY）

## ⚠️ 常见问题

### 问题1：部署失败
**可能原因：**
- `requirements.txt` 格式错误
- 依赖版本冲突
- Python 版本不兼容

**解决方案：**
- 检查 `requirements.txt` 格式
- 查看 Streamlit Cloud 的部署日志
- 确保所有依赖都是公开可用的

### 问题2：无法读取飞书数据
**可能原因：**
- Secrets 未正确配置
- API Key 无效
- 飞书应用权限不足

**解决方案：**
- 检查 Secrets 配置是否正确
- 验证 `FEISHU_APP_ID` 和 `FEISHU_APP_SECRET`
- 检查飞书应用权限设置

### 问题3：AI 生成功能不工作
**可能原因：**
- `LLM_API_KEY` 未配置或无效
- API Key 余额不足
- 模型名称错误

**解决方案：**
- 检查 Secrets 中的 `LLM_API_KEY`
- 验证 API Key 是否有效
- 确认模型名称是 `glm-4.6v`

### 问题4：配置文件保存失败
**说明：** 这是正常的！在 Streamlit Cloud 上，文件系统是只读的。

**解决方案：**
- 使用 Secrets 配置环境变量（推荐）
- 或使用 Session State（临时，刷新后丢失）

## 📝 注意事项

1. **安全性**
   - ✅ 所有敏感信息通过 Secrets 配置
   - ✅ `.feishu_config.json` 已在 `.gitignore` 中
   - ⚠️ 不要在代码中硬编码敏感信息

2. **性能**
   - Streamlit Cloud 免费版有资源限制
   - 大量数据生成可能需要较长时间
   - 建议分批生成或优化代码

3. **更新**
   - 每次 GitHub push 后，Streamlit Cloud 会自动重新部署
   - 修改 Secrets 后需要手动触发重新部署

## ✅ 部署完成标志

- [ ] 应用可以正常访问
- [ ] 能够读取飞书数据
- [ ] 能够选择学科和知识点
- [ ] 能够生成题库 WORD 文档
- [ ] 能够生成题库 HTML 文档
- [ ] 能够生成类似题目（如果配置了 LLM_API_KEY）
- [ ] 所有功能测试通过

---

**最后更新：** 2025-12-18
**版本：** v1.0

