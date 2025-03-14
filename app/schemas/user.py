import uuid
from typing import Optional
from datetime import datetime

from pydantic import BaseModel, Field, UUID4, EmailStr


# 共享属性
class UserBase(BaseModel):
    """
    用户基础模式
    """
    email: Optional[str] = None
    username: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None


# 创建用户时的属性
class UserCreate(UserBase):
    """
    创建用户模式
    """
    email: str
    username: str
    password: str


# 更新用户时的属性
class UserUpdate(UserBase):
    """
    更新用户模式
    """
    password: Optional[str] = None


# 密码重置请求
class PasswordResetRequest(BaseModel):
    """
    密码重置请求模式
    """
    email: str


# 密码重置确认
class PasswordResetConfirm(BaseModel):
    """
    密码重置确认模式
    """
    token: str
    new_password: str


# 密码修改
class PasswordChange(BaseModel):
    """
    密码修改模式
    """
    current_password: str
    new_password: str


# 数据库中的用户属性
class UserInDBBase(UserBase):
    """
    数据库中的用户基础模式
    """
    id: UUID4
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# 返回给API的用户属性
class User(UserInDBBase):
    """
    返回给API的用户模式
    """
    pass


# 存储在数据库中的用户附加属性
class UserInDB(UserInDBBase):
    """
    数据库中的用户模式（包含哈希密码）
    """
    hashed_password: str 