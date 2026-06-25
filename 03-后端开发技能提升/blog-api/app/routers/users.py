"""
用户路由 - RESTful API端点
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models.user import User as UserModel
from app.schemas.user import (
    UserCreate, UserUpdate, UserResponse, 
    Token, Message
)
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError

router = APIRouter()

# 密码哈希工具
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """生成密码哈希"""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """创建JWT访问令牌"""
    from app.config import settings
    
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


@router.post("/users/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    创建新用户
    
    - **email**: 用户邮箱（唯一）
    - **username**: 用户名（3-20字符，字母数字下划线）
    - **password**: 密码（至少8位）
    - **full_name**: 全名（可选）
    """
    # 检查邮箱是否已存在
    db_user = db.query(UserModel).filter(UserModel.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册"
        )
    
    # 检查用户名是否已存在
    db_user = db.query(UserModel).filter(UserModel.username == user.username).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户名已被使用"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        username=user.username,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: UserLogin, db: Session = Depends(get_db)):
    """
    用户登录并获取JWT令牌
    
    返回access_token用于后续认证请求
    """
    # 验证用户凭据
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 检查用户是否激活
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户账号已被禁用"
        )
    
    # 生成JWT令牌
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users/", response_model=List[UserResponse])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取用户列表
    
    - **skip**: 分页偏移量（默认0）
    - **limit**: 返回数量上限（默认100）
    """
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users


@router.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: UserModel = Depends(get_current_user)):
    """
    获取当前登录用户信息
    """
    return current_user


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    根据ID获取用户详情
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    更新用户信息
    
    只能更新自己的信息或管理员可更新任何人
    """
    # 权限检查：只能更新自己或管理员
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只能修改自己的信息"
        )
    
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    # 更新字段
    update_data = user_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    删除用户
    
    只能删除自己或管理员可删除任何用户
    """
    # 权限检查
    if current_user.id != user_id and not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="权限不足，只能删除自己的账号"
        )
    
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    
    if db_user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    db.delete(db_user)
    db.commit()
    
    return None


# 辅助函数：获取当前用户
async def get_current_user(token: str = Depends(oauth2_scheme()), db: Session = Depends(get_db)):
    """验证JWT令牌并返回当前用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无效的认证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(UserModel).filter(UserModel.username == username).first()
    
    if user is None:
        raise credentials_exception
    
    return user


# OAuth2密码流（简化版）
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")
