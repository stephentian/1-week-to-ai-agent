# 🎯 Day 7-8 实战项目：DocuMind AI 智能文档助手

> **项目名称**: documind-ai
> **项目描述**: 完整的AI Agent产品 - 基于RAG的智能文档问答系统
> **技术栈**: FastAPI + Vue3 + LangChain + DeepSeek + ChromaDB
> **毕业项目** ✨

---

## 📁 项目结构

```
documind-ai/
├── backend/                   # 后端服务 (FastAPI)
│   ├── main.py               # 应用入口
│   ├── config.py             # 配置管理
│   ├── agents/               # AI Agent模块
│   │   ├── researcher.py     # 研究员Agent（信息检索）
│   │   └── writer.py         # 写作者Agent（内容生成）
│   ├── rag_engine.py         # RAG检索增强生成引擎
│   └── tools/                # 工具函数
│       ├── document_parser.py    # 文档解析
│       └── vector_store.py      # 向量存储
│
├── frontend/                  # 前端界面 (Vue3)
│   └── src/
│       ├── views/
│       │   ├── ChatInterface.vue    # 聊天界面
│       │   └── DocumentUpload.vue   # 文档上传
│       └── App.vue           # 主应用组件
│
├── docker-compose.yml        # 全栈部署配置
├── .env.example              # 环境变量示例
└── README.md                 # 项目说明
```

---

## 🚀 快速开始

### 方式一：Docker一键部署（推荐）

```bash
# 1. 复制环境变量文件
cp .env.example .env

# 2. 编辑.env，填入API密钥
# DEEPSEEK_API_KEY=your-key-here

# 3. 启动所有服务
docker-compose up -d --build

# 4. 访问应用
# 前端界面: http://localhost:3000
# 后端API: http://localhost:8000/docs
```

### 方式二：本地开发运行

```bash
# 后端
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 前端（新终端）
cd frontend
npm install
npm run dev

# 访问 http://localhost:5173
```

---

## ✅ 核心功能清单

### 📄 文档管理
- [x] 多格式上传（PDF, Word, TXT, Markdown）
- [x] 智能文档解析和分块
- [x] 向量化存储（ChromaDB）
- [x] 文档列表和管理

### 💬 智能问答
- [x] 基于RAG的精准问答
- [x] 引用来源展示
- [x] 多轮对话支持
- [x] 上下文理解

### 🤖 AI Agent能力
- [x] 多Agent协作（研究员+写作者）
- [x] 自动摘要生成
- [x] 内容分析报告
- [x] Function Calling工具调用

### 🎨 用户界面
- [x] 现代化聊天界面
- [x] 实时流式输出
- [x] Markdown渲染
- [x] 响应式设计

---

## 🏗️ 架构设计

```
用户 → Vue3前端 → FastAPI后端 → LangChain框架
                              ↓
                    ┌─────────────────────┐
                    │   RAG Engine        │
                    ├─────────────────────┤
                    │ • Document Parser   │
                    │ • Vector Store      │
                    │ • Retriever         │
                    │ • LLM Chain         │
                    └─────────────────────┘
                              ↓
                    ┌─────────────────────┐
                    │   Multi-Agent System │
                    ├─────────────────────┤
                    │ • Researcher Agent  │
                    │ • Writer Agent      │
                    │ • Orchestrator      │
                    └─────────────────────┘
                              ↓
                    DeepSeek / 豆包 API
```

---

## 🎯 使用场景

1. **企业知识库问答**
 - 上传公司文档、手册、FAQ
 - 员工快速获取准确答案

2. **学习资料助手**
 - 导入课程笔记、教材
 - 智能答疑和知识点提取

3. **研究报告生成**
 - 上传多篇相关文献
 - 自动生成综述和分析

4. **技术文档查询**
 - API文档、代码注释
 - 快速定位解决方案

---

## 🔗 相关文档

本项目整合了整个一周的学习成果：
- ✅ **Day 1**: 开发环境搭建（Docker部署）
- ✅ **Day 2**: Vue3前端技术（聊天界面）
- ✅ **Day 3**: FastAPI后端开发（RESTful API）
- ✅ **Day 4**: 数据库技术（ChromaDB向量库）
- ✅ **Day 5**: 运维部署（生产级Docker配置）
- ✅ **Day 6**: AI基础应用（DeepSeek API集成）

---

## 🎓 项目价值

这是一个**完整可交付的AI产品**：

- ✅ 可作为**求职作品集**展示
- ✅ 可**上线运营**成为SaaS产品
- ✅ 可**开源**建立技术影响力
- ✅ 可作为**企业内部工具**提升效率

**恭喜完成从前后端开发者到AI工程师的蜕变！🎉**
