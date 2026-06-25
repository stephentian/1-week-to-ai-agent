# Day 6 实战项目：AI工具服务

> **项目名称**: ai-tools
> **项目描述**: 集成DeepSeek、豆包等国内大模型API的统一AI工具服务
> **技术栈**: Python + FastAPI + DeepSeek API + 豆包(火山引擎) API

---

## 📁 项目结构

```
ai-tools/
├── llm_service.py             # 统一LLM调用接口
├── deepseek_client.py         # DeepSeek客户端封装
├── doubao_client.py           # 豆包(火山引擎)客户端封装
├── prompts/                   # Prompt模板库
│   ├── summarization.txt      # 文本摘要模板
│   ├── translation.txt        # 翻译模板
│   └── code_generation.txt    # 代码生成模板
├── test_ai_api.py            # API测试脚本
├── requirements.txt          # Python依赖
└── README.md                 # 项目说明
```

---

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

创建`.env` 文件：

```bash
# DeepSeek API配置
DEEPSEEK_API_KEY=your-deepseek-api-key

# 豆包(火山引擎)API配置
DOUBAO_API_KEY=your-doubao-api-key
DOUBAO_APP_ID=your-app-id
```

### 3. 运行测试

```bash
python test_ai_api.py
```

---

## ✅ 功能清单

### 核心功能
- [x] DeepSeek API 对话、代码生成、情感分析
- [x] 豆包 API 对话、角色扮演、视觉理解
- [x] 统一的LLM服务层（智能路由）
- [x] Prompt Engineering 模板库
- [x] 多轮对话支持（上下文管理）
- [x] 错误处理和重试机制

### 技术特性
- [x] 异步请求支持
- [x] 流式输出（Streaming）
- [x] Token使用统计
- [x] 响应时间监控
- [x] 故障转移（Fallback）

---

## 📡 API端点（如果集成到FastAPI）

| 方法 | 端点 | 描述 |
|------|------|------|
| POST |`/api/chat` | 统一对话接口 |
| POST |`/api/chat/stream` | 流式对话 |
| POST |`/api/summarize` | 文本摘要 |
| POST |`/api/translate` | 文本翻译 |
| POST |`/api/generate-code` | 代码生成 |

---

## 🔗 相关文档

本项目对应 **Day 6** 的以下学习内容：
- 大语言模型基础原理
- DeepSeek API 实践应用
- 豆包(火山引擎) API 集成
- Prompt Engineering 设计技巧
- AI应用开发最佳实践

**下一步**: [Day 7: AI Agent核心技术与实战项目](../07-AI%20Agent核心技术与实战项目/README.md)
