"""
DocuMind AI - 智能文档助手后端服务
Day 7-8 实战项目：AI Agent 核心技术与实战项目
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import os
import shutil

from app.config import settings
from app.rag_engine import RAGEngine
from app.agents.researcher import ResearcherAgent
from app.agents.writer import WriterAgent


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    print("🚀 启动 DocuMind AI 服务...")
    
    # 初始化上传目录
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    os.makedirs(settings.CHROMA_PERSIST_DIR, exist_ok=True)
    
    # 初始化RAG引擎
    global rag_engine, researcher_agent, writer_agent
    
    rag_engine = RAGEngine()
    researcher_agent = ResearcherAgent(rag_engine)
    writer_agent = WriterAgent(rag_engine)
    
    print("✅ DocuMind AI 初始化完成")
    
    yield
    
    # 清理资源
    print("👋 正在关闭服务...")


# 创建FastAPI应用
app = FastAPI(
    title="DocuMind AI API",
    description="智能文档助手 - 基于RAG的AI问答系统",
    version="1.0.0",
    docs_url="/docs",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ===== 文档管理API =====

@app.post("/api/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    上传文档并处理
    
    - 支持格式: PDF, TXT, MD, DOCX
    - 自动解析、分块、向量化存储
    """
    # 验证文件类型
    file_ext = file.filename.split('.')[-1].lower()
    if file_ext not in settings.SUPPORTED_FORMATS:
        raise HTTPException(status_code=400, detail=f"不支持的文件格式: {file_ext}")
    
    # 验证文件大小
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail=f"文件过大，最大支持{settings.MAX_UPLOAD_SIZE_MB}MB")
    
    # 保存文件
    file_path = os.path.join(settings.UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(content)
    
    try:
        # 处理文档（解析+向量化）
        doc_id = rag_engine.process_document(file_path, file.filename)
        
        return {
            "success": True,
            "document_id": doc_id,
            "filename": file.filename,
            "message": "文档上传成功，已建立索引"
        }
        
    except Exception as e:
        # 清理失败的文件
        if os.path.exists(file_path):
            os.remove(file_path)
        
        raise HTTPException(status_code=500, detail=f"文档处理失败: {str(e)}")


@app.get("/api/documents")
async def list_documents():
    """获取已上传的文档列表"""
    documents = rag_engine.list_documents()
    return {"documents": documents}


@app.delete("/api/documents/{doc_id}")
async def delete_document(doc_id: str):
    """删除文档及其向量数据"""
    success = rag_engine.delete_document(doc_id)
    
    if success:
        return {"success": True, "message": "文档删除成功"}
    else:
        raise HTTPException(status_code=404, detail="文档不存在")


# ===== 智能问答API =====

@app.post("/api/chat")
async def chat(request: dict):
    """
    智能问答接口
    
    支持基于文档内容的精准问答，使用RAG技术
    """
    question = request.get("question")
    doc_ids = request.get("doc_ids", [])  # 可选：指定查询的文档范围
    conversation_history = request.get("history", [])
    
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    try:
        # 使用研究员Agent进行检索和回答
        result = researcher_agent.query(
            question=question,
            doc_ids=doc_ids,
            history=conversation_history
        )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"问答失败: {str(e)}")


@app.post("/api/chat/stream")
async def chat_stream(request: dict):
    """
    流式问答接口（Server-Sent Events）
    
    实时返回生成过程，提升用户体验
    """
    from fastapi.responses import StreamingResponse
    import json
    
    question = request.get("question")
    
    if not question:
        raise HTTPException(status_code=400, detail="问题不能为空")
    
    async def generate():
        # 流式生成回答
        for chunk in researcher_agent.stream_query(question):
            yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        
        yield "data: [DONE]\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


# ===== 高级功能API =====

@app.post("/api/summarize")
async def summarize_document(request: dict):
    """
    生成文档摘要
    
    使用写作者Agent对指定文档进行智能摘要
    """
    doc_id = request.get("document_id")
    
    if not doc_id:
        raise HTTPException(status_code=400, detail="缺少document_id参数")
    
    summary = writer_agent.summarize_document(doc_id)
    
    return {
        "success": True,
        "summary": summary,
        "document_id": doc_id
    }


@app.post("/api/analyze")
async def analyze_documents(request: dict):
    """
    多文档分析报告
    
    对多个文档进行综合分析，生成报告
    """
    doc_ids = request.get("doc_ids", [])
    analysis_type = request.get("type", "general")  # general, compare, extract
    
    if not doc_ids:
        raise HTTPException(status_code=400, detail="请提供至少一个文档ID")
    
    report = writer_agent.generate_analysis_report(doc_ids, analysis_type)
    
    return {
        "success": True,
        "report": report,
        "documents_analyzed": len(doc_ids),
        "analysis_type": analysis_type
    }


# ===== 系统状态API =====

@app.get("/")
async def root():
    """根路径"""
    return {
        "service": "DocuMind AI",
        "version": "1.0.0",
        "description": "智能文档助手 - 基于RAG的AI问答系统",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    status = {
        "status": "healthy",
        "service": "documind-ai-backend",
        "components": {}
    }
    
    # 检查各组件状态
    try:
        status["components"]["rag_engine"] = rag_engine.health_check()
    except:
        status["components"]["rag_engine"] = "error"
    
    try:
        status["components"]["llm_service"] = researcher_agent.llm_client is not None
    except:
        status["components"]["llm_service"] = False
    
    return status


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════╗
║     🧠 DocuMind AI - 智能文档助手         ║
║     Day 7-8 AI Agent 实战项目             ║
╠════════════════════════════════════════╣
║     API: http://localhost:8000           ║
║     Docs: http://localhost:8000/docs      ║
╚════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True
    )
