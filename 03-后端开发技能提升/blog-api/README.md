# Day 3 实战项目：博客 REST API

> **项目名称**: blog-api
> **项目描述**: 使用FastAPI构建的生产级博客后端API服务
> **技术栈**: Python 3.11 + FastAPI + SQLAlchemy + SQLite/PostgreSQL

---

## 📁 项目结构

```
blog-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI应用入口
│   ├── config.py               # 配置管理
│   ├── database.py             # 数据库连接
│   ├── models/                 # SQLAlchemy数据模型
│   │   ├── __init__.py
│   │   └── user.py            # 用户模型
│   ├── schemas/                # Pydantic请求/响应模型
│   │   ├── __init__.py
│   │   └── user.py            # 用户相关schema
│   └── routers/                # 路由模块
│       ├── __init__.py
│       └── users.py           # 用户路由
├── tests/
│   └── test_users.py          # 用户接口测试
├── requirements.txt           # Python依赖
├── Dockerfile                 # 容器化配置
└── README.md                  # 项目说明
```

---

## 🚀 快速开始

### 方式一：本地运行

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行服务器
uvicorn app.main:app --reload --port 8000

# 访问API文档
# http://localhost:8000/docs (Swagger UI)
# http://localhost:8000/redoc (ReDoc)
```

### 方式二：Docker运行

```bash
# 构建并运行
docker build -t blog-api .
docker run -p 8000:8000 blog-api

# 或使用docker-compose（如果有的话）
docker-compose up -d
```

---

## ✅ 功能清单

### 核心功能
- [x] 用户注册（POST /users/）
- [x] 用户登录（POST /token）
- [x] 获取用户列表（GET /users/）
- [x] 获取单个用户（GET /users/{id}）
- [x] 更新用户信息（PUT /users/{id}）
- [x] 删除用户（DELETE /users/{id}）
- [x] 自动生成API文档（Swagger UI）

### 技术特性
- [x] RESTful API设计
- [x] Pydantic数据验证
- [x] SQLAlchemy ORM
- [x] JWT身份认证
- [x] 异步编程支持
- [x] 错误处理中间件
- [x] CORS跨域支持
- [x] 单元测试覆盖

---

## 📡 API端点

### 用户管理

| 方法 | 端点 | 描述 | 认证 |
|------|------|------|------|
| POST |`/api/users/` | 注册新用户 | 否 |
| POST |`/api/token` | 登录获取Token | 否 |
| GET |`/api/users/` | 获取用户列表 | 是 |
| GET |`/api/users/me` | 获取当前用户信息 | 是 |
| GET |`/api/users/{id}` | 根据ID获取用户 | 是 |
| PUT |`/api/users/{id}` | 更新用户信息 | 是 |
| DELETE |`/api/users/{id}` | 删除用户 | 是 |

---

## 🔗 相关文档

本项目对应 **Day 3** 的以下学习内容：
- Python高级特性（装饰器、异步、上下文管理器）
- FastAPI框架核心概念
- RESTful API设计原则
- Pydantic数据验证
- ORM数据库操作

**下一步**: [Day 4: 数据库技术应用](../04-数据库技术应用/README.md)
