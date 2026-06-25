"""
AI Agent Starter - FastAPI 后端服务
一个完整的 AI Agent 开发环境模板
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

app = FastAPI(
    title="AI Agent Starter API",
    description="AI Agent 开发环境模板 - 后端API服务",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 中间件配置（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """根路径 - 欢迎信息"""
    return {
        "message": "Welcome to AI Agent Starter!",
        "status": "running",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {
        "status": "healthy",
        "service": "ai-agent-starter-backend",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development")
    }


@app.get("/api/info")
async def get_info():
    """获取系统信息"""
    import platform
    import sys
    
    return {
        "python_version": platform.python_version(),
        "platform": platform.system(),
        "architecture": platform.machine(),
        "api_version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    
    print("""
    ╔════════════════════════════════════════╗
    ║     🚀 AI Agent Starter Backend         ║
    ║     Starting server...                  ║
    ╠════════════════════════════════════════╣
    ║     API: http://localhost:8000          ║
    ║     Docs: http://localhost:8000/docs    ║
    ╚════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
