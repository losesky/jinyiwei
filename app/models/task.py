import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Task(Base):
    """
    任务模型，用于跟踪Celery任务
    """
    # 任务ID (Celery任务ID)
    task_id: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    
    # 任务名称
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    # 任务状态 (PENDING, STARTED, SUCCESS, FAILURE, RETRY, REVOKED)
    status: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    
    # 任务参数
    args: Mapped[Optional[List[Any]]] = mapped_column(JSONB, nullable=True)
    
    # 任务关键字参数
    kwargs: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # 任务结果
    result: Mapped[Optional[Any]] = mapped_column(JSONB, nullable=True)
    
    # 任务错误信息
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 任务开始时间
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 任务完成时间
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 任务执行时间（秒）
    execution_time: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # 任务重试次数
    retries: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # 任务优先级
    priority: Mapped[int] = mapped_column(Integer, default=5, nullable=False)
    
    # 任务所属用户ID
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    
    # 关联用户
    user: Mapped[Optional["User"]] = relationship("User", backref="tasks") 