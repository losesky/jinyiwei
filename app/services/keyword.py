from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.keyword import Keyword
from app.schemas.keyword import KeywordCreate, KeywordUpdate


async def get_keyword(db: AsyncSession, *, keyword_id: UUID) -> Optional[Keyword]:
    """
    通过ID获取关键词
    """
    result = await db.execute(select(Keyword).where(Keyword.id == keyword_id))
    return result.scalars().first()


async def get_keywords(
    db: AsyncSession, *, user_id: Optional[UUID] = None, skip: int = 0, limit: int = 100, is_active: Optional[bool] = None
) -> List[Keyword]:
    """
    获取关键词列表
    
    Args:
        db: 数据库会话
        user_id: 用户ID，如果为None则获取所有用户的关键词
        skip: 跳过的记录数
        limit: 返回的最大记录数
        is_active: 是否只返回活跃的关键词
    
    Returns:
        关键词列表
    """
    query = select(Keyword)
    
    # 如果指定了用户ID，则只返回该用户的关键词
    if user_id is not None:
        query = query.where(Keyword.user_id == user_id)
    
    # 如果指定了is_active，则只返回活跃/非活跃的关键词
    if is_active is not None:
        query = query.where(Keyword.is_active == is_active)
    
    # 分页
    query = query.offset(skip).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def create_keyword(
    db: AsyncSession, *, keyword_in: KeywordCreate, user_id: UUID
) -> Keyword:
    """
    创建新关键词
    """
    db_obj = Keyword(
        text=keyword_in.text,
        description=keyword_in.description,
        is_active=keyword_in.is_active,
        priority=keyword_in.priority,
        user_id=user_id,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def update_keyword(
    db: AsyncSession, *, db_obj: Keyword, obj_in: Union[KeywordUpdate, Dict[str, Any]]
) -> Keyword:
    """
    更新关键词
    """
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def delete_keyword(db: AsyncSession, *, keyword_id: UUID) -> Keyword:
    """
    删除关键词
    """
    result = await db.execute(select(Keyword).where(Keyword.id == keyword_id))
    keyword = result.scalars().first()
    await db.delete(keyword)
    await db.commit()
    return keyword 