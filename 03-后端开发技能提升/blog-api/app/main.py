"""
Blog API - FastAPI应用入口
Day 3 实战项目：后端开发技能提升
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from app.config import settings
from app.database import engine, Base
from app.routers import users


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时：创建数据库表
    print("🚀 启动 Blog API 服务...")
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库初始化完成")
    
    yield
    
    # 关闭时：清理资源
    print("👋 正在关闭服务...")


# 创建FastAPI应用
app = FastAPI(
    title="Blog API",
    description="基于FastAPI的博客后端API - Day 3实战项目",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS中间件配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(users.router, prefix="/api", tags=["Users"])


@app.get("/")
async def root():
    """根路径 - API信息"""
    return {
        "message": "Welcome to Blog API",
        "service": "blog-api",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "blog-api",
        "database": "connected"
    }


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     📝 Blog API - FastAPI Backend         ║
║     Day 3 实战项目                       ║
╠════════════════════════════════════════╣
║     API: http://localhost:8000           ║
║     Docs: http://localhost:8000/docs     ║
╚════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
