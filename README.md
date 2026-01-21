# 飞书错题本 v1.0

从飞书多维表格读取错题数据，支持智能练习和生成试卷。

## 在线使用

**Streamlit Cloud**: https://cuoti-shijuan.streamlit.app

## 功能介绍

### 主界面

应用启动后显示两个主要功能按钮：

| 功能 | 说明 |
|------|------|
| **错题练习** | 根据艾宾浩斯遗忘曲线智能复习错题 |
| **生成试卷** | 选择学科和知识点生成试卷文档 |

---

### 1. 错题练习

基于艾宾浩斯遗忘曲线的智能复习系统。

**功能特点**：
- 按下次复习时间自动选题
- 支持"会了/不会"反馈
- 不会时自动生成类似题强化练习
- 练习记录自动保存到飞书

**使用流程**：
1. 选择学科和知识点筛选范围
2. 点击"开始练习"
3. 查看题目后选择"会了"或"不会"
4. 系统自动安排下次复习时间

---

### 2. 生成试卷

支持生成原题试卷和AI生成的类似题试卷。

**生成原题试卷**：
- 从错题库随机抽取题目
- 支持 Word 和 HTML 两种格式

**生成类似题试卷**：
- 基于智谱AI GLM-4.6V生成
- 支持图片题目识别
- 保持相同知识点和难度

---

## 配置说明

### Streamlit Cloud Secrets 配置

在 Streamlit Cloud 的 Settings → Secrets 中添加：

```toml
[secrets]
FEISHU_APP_ID = "你的飞书应用ID"
FEISHU_APP_SECRET = "你的飞书应用Secret"
FEISHU_APP_TOKEN = "NO9nbcpjraKeUCsSQkBcHL9gnhh"
FEISHU_TABLE_ID = "tblchSd315sqHTCt"
FEISHU_PRACTICE_TABLE_ID = "tbll3uQ4iL4LsVks"
LLM_API_KEY = "你的智谱AI API Key"
LLM_API_BASE = "https://open.bigmodel.cn/api/paas/v4"
LLM_MODEL = "glm-4.6v"
```

### 本地配置

本地运行时，配置保存在 `.feishu_config.json` 文件中。

### 配置项说明

| 配置项 | 必填 | 说明 |
|--------|------|------|
| FEISHU_APP_ID | ✅ | 飞书应用 App ID |
| FEISHU_APP_SECRET | ✅ | 飞书应用 App Secret |
| FEISHU_APP_TOKEN | ✅ | 多维表格 app_token |
| FEISHU_TABLE_ID | ✅ | 错题表 table_id |
| FEISHU_PRACTICE_TABLE_ID | ⚠️ | 练习记录表 table_id（错题练习功能需要） |
| LLM_API_KEY | ⚠️ | 智谱AI API Key（类似题功能需要） |
| LLM_API_BASE | - | 智谱AI API地址（默认自动设置） |
| LLM_MODEL | - | 模型名称（默认 glm-4.6v） |

---

## 飞书表格字段

### 错题表字段

| 字段名 | 说明 |
|--------|------|
| 学科 | 错题所属学科 |
| 知识点 | 涉及的知识点（支持多选） |
| 去手写 | 题目内容（支持图片附件） |
| 不会/做错 | 错题类型 |
| 不会/做错原因 | 详细错因 |

### 练习记录表字段

| 字段名 | 说明 |
|--------|------|
| 错题record_id | 关联的错题ID |
| 上次练习时间 | 毫秒时间戳 |
| 掌握程度 | "会"或"不会" |
| 练习次数 | 累计练习次数 |
| 下次练习时间 | 毫秒时间戳 |

---

## 本地运行

### 安装依赖

```bash
pip install -r requirements.txt
```

### 启动应用

```bash
streamlit run app.py
```

或双击 `启动程序.bat`

---

## 技术栈

- **前端**: Streamlit
- **文档生成**: python-docx
- **AI模型**: 智谱AI GLM-4.6V
- **数据源**: 飞书多维表格 API

---

## 更新日志

### v1.0 (2025-01)
- 简化主界面：两个功能按钮（错题练习、生成试卷）
- 错题练习：艾宾浩斯遗忘曲线智能复习
- 生成试卷：原题试卷 + AI类似题试卷
- 支持 Word 和 HTML 两种格式
- 智谱AI GLM-4.6V 多模态支持
