# 如何查看 Streamlit Cloud 部署日志（正确方法）

## 📋 正确步骤

### 方法1：通过应用页面的 "Manage app" 菜单（推荐）

1. **访问你的应用**
   - 打开你的应用 URL：`https://cuoti-shijuan.streamlit.app`
   - 或者从 Streamlit Cloud 主页点击应用链接

2. **打开 "Manage app" 菜单**
   - 在应用页面的**右下角**，找到 **"Manage app"** 按钮
   - 点击这个按钮

3. **查看日志**
   - 在弹出的菜单中，选择 **"Logs"** 选项
   - 这里会显示所有的部署日志和运行时日志

4. **下载日志（可选）**
   - 在日志页面底部，点击 **"⋮"（三个点）** 菜单
   - 选择 **"Download log"** 可以下载日志文件

---

### 方法2：从 Streamlit Cloud 主页进入

1. **访问 Streamlit Cloud**
   - 打开：https://share.streamlit.io/
   - 登录你的账号

2. **找到你的应用**
   - 在应用列表中找到你的应用
   - 点击应用卡片上的链接进入应用页面

3. **按照方法1的步骤2-3操作**

---

## 🔍 日志内容

在 Logs 页面中，你会看到：

### 部署日志
- ✅ 依赖安装过程（`pip install`）
- ✅ 代码编译信息
- ✅ 应用启动信息
- ❌ 构建错误（如果有）

### 运行时日志
- ✅ 应用运行时的输出
- ✅ Python 错误和异常
- ✅ API 调用日志（如果有）
- ❌ 运行时错误

---

## ⚠️ 注意事项

1. **"Manage app" 按钮位置**
   - 在应用页面的**右下角**
   - 需要滚动到页面底部才能看到
   - 或者使用快捷键定位

2. **权限要求**
   - 只有应用的所有者才能查看日志
   - 确保你已登录正确的账号

3. **日志实时更新**
   - 日志会实时更新
   - 如果应用正在部署，可以看到实时部署进度

---

## 📊 日志示例

### 正常部署日志
```
Collecting streamlit
  Downloading streamlit-1.28.0-py3-none-any.whl
Successfully installed streamlit-1.28.0 requests-2.31.0

You can now view your Streamlit app in your browser.
```

### 错误日志
```
File "/mount/src/cuoti_shijuan/app.py", line 123, in main
    token = get_tenant_access_token(app_id, app_secret)
RuntimeError: 获取 tenant_access_token 失败
```

---

## 🔧 如果找不到 "Manage app" 按钮

### 检查清单
- [ ] 是否在应用页面（不是设置页面）？
- [ ] 是否滚动到页面底部？
- [ ] 是否已登录正确的账号？
- [ ] 应用是否正在运行？

### 替代方法

如果仍然找不到，可以：

1. **查看应用页面上的错误信息**
   - 如果有错误，通常会直接显示在页面上
   - 这些错误信息通常包含详细的堆栈跟踪

2. **使用浏览器开发者工具**
   - 按 `F12` 打开开发者工具
   - 切换到 "Console" 标签页
   - 查看是否有 JavaScript 错误或网络请求失败

3. **检查应用状态**
   - 回到 Streamlit Cloud 主页
   - 查看应用的状态图标（绿色/黄色/红色）
   - 红色表示有错误

---

## 💡 提示

1. **日志是排查问题的关键**
   - 遇到问题时，首先查看日志
   - 日志会告诉你具体哪里出了问题

2. **下载日志进行分析**
   - 如果日志很长，可以下载到本地
   - 使用文本编辑器或日志分析工具查看

3. **关注错误信息**
   - 查找 `ERROR`、`Exception`、`Traceback` 等关键词
   - 这些是定位问题的关键

---

**重要提示：** 日志在 **"Manage app"** 菜单中，**不在 Settings 页面**！
