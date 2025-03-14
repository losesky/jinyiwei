from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, UUID4, Field, HttpUrl


# 共享属性
class NewsBase(BaseModel):
    """
    新闻基础模式
    """
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    url: Optional[str] = None
    source: Optional[str] = None
    published_at: Optional[datetime] = None
    author: Optional[str] = None
    sentiment_score: Optional[float] = None
    meta_data: Optional[Dict[str, Any]] = None


# 创建新闻时的属性
class NewsCreate(NewsBase):
    """
    创建新闻模式
    """
    title: str
    url: str
    source: str
    crawled_at: datetime = Field(default_factory=datetime.utcnow)


# 更新新闻时的属性
class NewsUpdate(NewsBase):
    """
    更新新闻模式
    """
    pass


# 数据库中的新闻属性
class NewsInDBBase(NewsBase):
    """
    数据库中的新闻基础模式
    """
    id: UUID4
    crawled_at: datetime
    
    class Config:
        from_attributes = True


# 返回给API的新闻属性
class News(NewsInDBBase):
    """
    返回给API的新闻模式
    """
    pass


# 存储在数据库中的新闻附加属性
class NewsInDB(NewsInDBBase):
    """
    数据库中的新闻模式
    """
    pass


# 新闻搜索参数
class NewsSearchParams(BaseModel):
    """
    新闻搜索参数
    """
    keyword: Optional[str] = None
    source: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    sentiment_min: Optional[float] = None
    sentiment_max: Optional[float] = None
    limit: int = 50
    offset: int = 0 