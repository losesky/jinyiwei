from typing import Optional
from datetime import datetime

from sqlalchemy import Boolean, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base_class import Base


class User(Base):
    """
    用户模型
    """
    # 指定表名，避免使用PostgreSQL保留字
    __tablename__ = "users"
    
    # 用户名，唯一
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    
    # 电子邮件，唯一
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    
    # 密码哈希
    hashed_password: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # 全名
    full_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 是否激活
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 是否超级用户
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # 密码重置令牌
    reset_token: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 密码重置令牌过期时间
    reset_token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 上次登录时间
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 登录尝试次数
    login_attempts: Mapped[int] = mapped_column(default=0, nullable=False) 