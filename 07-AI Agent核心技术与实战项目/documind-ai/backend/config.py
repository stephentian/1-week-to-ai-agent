"""
DocuMind AI 配置管理
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """应用配置类"""
    
    # 应用信息
    APP_NAME: str = "DocuMind AI"
    DEBUG: bool = True
    SECRET_KEY: str = "documind-secret-key-2026"
    
    # DeepSeek API
    DEEPSEEK_API_KEY: str = ""
    
    # 豆包API（可选）
    DOUBAO_API_KEY: str = ""
    DOUBAO_APP_ID: str = ""
    
    # 数据库
    DATABASE_URL: str = "sqlite:///./documind.db"
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # ChromaDB向量库
    CHROMA_PERSIST_DIR: str = "./chroma_db"
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    # 文件上传
    MAX_UPLOAD_SIZE_MB: int = 50
    UPLOAD_DIR: str = "./uploads"
    SUPPORTED_FORMATS: str = "pdf,txt,md,docx"
    
    @property
    def supported_formats_list(self) -> List[str]:
        return [fmt.strip().lower() for fmt in self.SUPPORTED_FORMATS.split(",")]
    
    # RAG配置
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    TOP_K_RETRIEVAL: int = 5
    SIMILARITY_THRESHOLD: float = 0.7
    
    class Config:
        env_file = ".env"


settings = Settings()
