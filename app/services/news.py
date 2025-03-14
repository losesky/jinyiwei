from datetime import datetime
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select, and_, or_, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.news import News, news_keyword
from app.models.keyword import Keyword
from app.schemas.news import NewsCreate, NewsUpdate, NewsSearchParams


async def get_news(db: AsyncSession, *, news_id: UUID) -> Optional[News]:
    """
    通过ID获取新闻
    """
    result = await db.execute(
        select(News)
        .where(News.id == news_id)
        .options(selectinload(News.keywords))
    )
    return result.scalars().first()


async def get_news_by_url(db: AsyncSession, *, url: str) -> Optional[News]:
    """
    通过URL获取新闻
    """
    result = await db.execute(select(News).where(News.url == url))
    return result.scalars().first()


async def get_news_list(
    db: AsyncSession, *, skip: int = 0, limit: int = 100
) -> List[News]:
    """
    获取新闻列表
    """
    result = await db.execute(
        select(News)
        .order_by(desc(News.published_at))
        .offset(skip)
        .limit(limit)
        .options(selectinload(News.keywords))
    )
    return result.scalars().all()


async def search_news(
    db: AsyncSession, *, params: NewsSearchParams
) -> List[News]:
    """
    搜索新闻
    """
    query = select(News).options(selectinload(News.keywords))
    
    # 构建查询条件
    conditions = []
    
    if params.keyword:
        # 关键词搜索（标题或内容）
        keyword_condition = or_(
            News.title.ilike(f"%{params.keyword}%"),
            News.content.ilike(f"%{params.keyword}%")
        )
        conditions.append(keyword_condition)
    
    if params.source:
        conditions.append(News.source == params.source)
    
    if params.start_date:
        conditions.append(News.published_at >= params.start_date)
    
    if params.end_date:
        conditions.append(News.published_at <= params.end_date)
    
    if params.sentiment_min is not None:
        conditions.append(News.sentiment_score >= params.sentiment_min)
    
    if params.sentiment_max is not None:
        conditions.append(News.sentiment_score <= params.sentiment_max)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    # 排序、分页
    query = query.order_by(desc(News.published_at)).offset(params.offset).limit(params.limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_news_by_keyword(
    db: AsyncSession, *, keyword_id: UUID, skip: int = 0, limit: int = 100
) -> List[News]:
    """
    获取与关键词相关的新闻
    """
    result = await db.execute(
        select(News)
        .join(news_keyword)
        .where(news_keyword.c.keyword_id == keyword_id)
        .order_by(desc(News.published_at))
        .offset(skip)
        .limit(limit)
        .options(selectinload(News.keywords))
    )
    return result.scalars().all()


async def create_news(
    db: AsyncSession, *, news_in: NewsCreate, keyword_ids: Optional[List[UUID]] = None
) -> News:
    """
    创建新闻
    """
    # 检查URL是否已存在
    existing_news = await get_news_by_url(db, url=news_in.url)
    if existing_news:
        return existing_news
    
    # 创建新闻对象
    db_obj = News(
        title=news_in.title,
        content=news_in.content,
        summary=news_in.summary,
        url=news_in.url,
        source=news_in.source,
        published_at=news_in.published_at,
        author=news_in.author,
        sentiment_score=news_in.sentiment_score,
        meta_data=news_in.meta_data,
        crawled_at=news_in.crawled_at,
    )
    
    # 添加关键词关联
    if keyword_ids:
        keywords = await db.execute(
            select(Keyword).where(Keyword.id.in_(keyword_ids))
        )
        db_obj.keywords = keywords.scalars().all()
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_news(
    db: AsyncSession, *, db_obj: News, obj_in: Union[NewsUpdate, Dict[str, Any]]
) -> News:
    """
    更新新闻
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in update_data:
        if field != "keywords" and hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_news(db: AsyncSession, *, news_id: UUID) -> News:
    """
    删除新闻
    """
    result = await db.execute(select(News).where(News.id == news_id))
    news = result.scalars().first()
    await db.delete(news)
    await db.commit()
    return news


async def add_keyword_to_news(
    db: AsyncSession, *, news_id: UUID, keyword_id: UUID
) -> News:
    """
    为新闻添加关键词
    """
    news = await get_news(db, news_id=news_id)
    keyword = await db.execute(select(Keyword).where(Keyword.id == keyword_id))
    keyword = keyword.scalars().first()
    
    if news and keyword:
        news.keywords.append(keyword)
        db.add(news)
        await db.commit()
        await db.refresh(news)
    
    return news


async def remove_keyword_from_news(
    db: AsyncSession, *, news_id: UUID, keyword_id: UUID
) -> News:
    """
    从新闻中移除关键词
    """
    news = await get_news(db, news_id=news_id)
    
    if news:
        news.keywords = [k for k in news.keywords if str(k.id) != str(keyword_id)]
        db.add(news)
        await db.commit()
        await db.refresh(news)
    
    return news 