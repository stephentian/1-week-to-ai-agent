# Day 1 实战项目：AI Agent 开发环境搭建

> **项目名称**: ai-agent-starter  
> **项目描述**: 一个完整的AI Agent开发环境模板，集成前后端开发和Docker容器化

---

## 📁 项目结构

```
starter-project/
├── backend/                    # Python FastAPI 后端
│   ├── main.py                # FastAPI 应用入口
│   ├── requirements.txt       # Python 依赖
│   └── Dockerfile             # 后端容器化
│
├── frontend/                  # Vue3 前端
│   ├── package.json           # Node.js 依赖
│   ├── vite.config.js         # Vite 配置
│   ├── index.html             # HTML 入口
│   └── Dockerfile             # 前端容器化
│
├── docker/                    # Docker 配置
│   └── docker-compose.yml     # 多服务编排
│
├── .gitignore                 # Git 忽略规则
└── README.md                  # 项目说明
```

---

## 🚀 快速开始

### 方式一：传统方式运行

```bash
# 1. 启动后端服务
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 2. 新开终端，启动前端服务
cd frontend
npm install
npm run dev

# 3. 访问
# 后端 API: http://localhost:8000
# 前端页面: http://localhost:5173
# API 文档: http://localhost:8000/docs
```

### 方式二：Docker 一键启动（推荐）

```bash
cd docker
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f

# 访问
# 前端: http://localhost:3000
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs

# 停止服务
docker-compose down
```

---

## ✅ 功能验证清单

### 后端验证
- [ ] `http://localhost:8000` 返回欢迎信息
- [ ] `http://localhost:8000/health` 返回健康状态
- [ ] `http://localhost:8000/docs` 显示 Swagger UI 文档

### 前端验证
- [ ] `http://localhost:5173` 或 `http://localhost:3000` 显示前端页面
- [ ] 页面标题显示正确
- [ ] 能看到"Hello AI Agent!"文字

### Docker 验证
- [ ] `docker-compose up -d` 成功启动所有服务
- [ ] `docker-compose ps` 显示所有容器运行中
- [ ] 所有服务均可正常访问

---

## 📝 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.11+ | 后端开发 |
| FastAPI | 0.109+ | Web框架 |
| Uvicorn | ASGI服务器 | 运行FastAPI |
| Node.js | 18+ | 前端构建工具链 |
| Vue3 | 3.4+ | 前端框架 |
| Vite | 5.0+ | 构建工具 |
| Docker | 20+ | 容器化部署 |
| Docker Compose | 2.0+ | 多容器编排 |

---

## 🔧 环境要求

- **操作系统**: Windows 10+, macOS, Linux
- **Python**: 3.11 或更高版本
- **Node.js**: 18 LTS 或更高版本
- **Docker**: 20.10+ (可选，用于容器化部署)
- **Git**: 2.30+ (用于版本控制)

---

## 📖 下一步

完成本项目搭建后，你已具备：
✅ Git 版本控制能力  
✅ Python 开发环境  
✅ Node.js 前端环境  
✅ Docker 容器化能力  

**继续学习**: [Day 2: 前端技术复习与强化](../02-前端技术复习与强化/README.md)
