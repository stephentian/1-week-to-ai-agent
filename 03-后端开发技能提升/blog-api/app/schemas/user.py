"""
用户相关的Pydantic Schema
用于请求验证和响应序列化
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


# ===== 请求Schema =====

class UserCreate(BaseModel):
    """创建用户的请求模型"""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = Field(None, max_length=100)


class UserLogin(BaseModel):
    """用户登录的请求模型"""
    username: str
    password: str


class UserUpdate(BaseModel):
    """更新用户信息的请求模型"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


# ===== 响应Schema =====

class UserResponse(BaseModel):
    """用户信息的响应模型"""
    id: int
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT Token响应模型"""
    access_token: str
    token_type: str = "bearer"


class Message(BaseModel):
    """通用消息响应模型"""
    message: str
