from typing import Optional
from pydantic import BaseModel, UUID4, Field


# 共享属性
class KeywordBase(BaseModel):
    """
    关键词基础模式
    """
    text: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = True
    priority: Optional[str] = "3"


# 创建关键词时的属性
class KeywordCreate(KeywordBase):
    """
    创建关键词模式
    """
    text: str


# 更新关键词时的属性
class KeywordUpdate(KeywordBase):
    """
    更新关键词模式
    """
    pass


# 数据库中的关键词属性
class KeywordInDBBase(KeywordBase):
    """
    数据库中的关键词基础模式
    """
    id: UUID4
    user_id: UUID4
    
    class Config:
        from_attributes = True


# 返回给API的关键词属性
class Keyword(KeywordInDBBase):
    """
    返回给API的关键词模式
    """
    pass


# 存储在数据库中的关键词附加属性
class KeywordInDB(KeywordInDBBase):
    """
    数据库中的关键词模式
    """
    pass 