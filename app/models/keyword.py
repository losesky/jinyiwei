import uuid
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


class Keyword(Base):
    """
    关键词模型
    """
    # 关键词文本
    text: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    # 关键词描述
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 是否激活
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # 优先级 (1-5，5为最高)
    priority: Mapped[str] = mapped_column(String(1), default="3", nullable=False)
    
    # 所属用户ID
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    # 关联用户
    user: Mapped["User"] = relationship("User", backref="keywords") 