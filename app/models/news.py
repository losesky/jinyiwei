from datetime import datetime
from typing import Dict, List, Optional, Any

from sqlalchemy import Column, DateTime, ForeignKey, String, Text, Float, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base


# 关键词与新闻的多对多关系表
news_keyword = Table(
    "news_keyword",
    Base.metadata,
    Column("news_id", UUID(as_uuid=True), ForeignKey("news.id"), primary_key=True),
    Column("keyword_id", UUID(as_uuid=True), ForeignKey("keyword.id"), primary_key=True),
)


class News(Base):
    """
    新闻模型
    """
    # 标题
    title: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    
    # 内容
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 摘要
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # 来源URL
    url: Mapped[str] = mapped_column(String(512), unique=True, index=True, nullable=False)
    
    # 来源网站
    source: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    
    # 发布时间
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    
    # 抓取时间
    crawled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    # 作者
    author: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # 情感分析结果 (-1.0 到 1.0，负面到正面)
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    
    # 元数据 (JSON格式，存储额外信息)
    meta_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    
    # 关联的关键词
    keywords: Mapped[List["Keyword"]] = relationship("Keyword", secondary=news_keyword, backref="news_items") 