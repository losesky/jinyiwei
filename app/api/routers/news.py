from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user, get_current_active_superuser
from app.db.session import get_db
from app.models.user import User
from app.schemas.news import News, NewsCreate, NewsUpdate, NewsSearchParams
from app.services.news import (
    create_news,
    delete_news,
    get_news,
    get_news_list,
    search_news,
    update_news,
    get_news_by_keyword,
    add_keyword_to_news,
    remove_keyword_from_news,
)

router = APIRouter()


@router.get("/", response_model=List[News])
async def read_news(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取新闻列表
    """
    news = await get_news_list(db, skip=skip, limit=limit)
    return news


@router.post("/search", response_model=List[News])
async def search_news_items(
    *,
    db: AsyncSession = Depends(get_db),
    params: NewsSearchParams,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    搜索新闻
    """
    news = await search_news(db, params=params)
    return news


@router.get("/keyword/{keyword_id}", response_model=List[News])
async def read_news_by_keyword(
    *,
    db: AsyncSession = Depends(get_db),
    keyword_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取与关键词相关的新闻
    """
    news = await get_news_by_keyword(db, keyword_id=keyword_id, skip=skip, limit=limit)
    return news


@router.post("/", response_model=News)
async def create_news_item(
    *,
    db: AsyncSession = Depends(get_db),
    news_in: NewsCreate,
    keyword_ids: List[UUID] = Query(None),
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    创建新闻（仅限管理员）
    """
    news = await create_news(db, news_in=news_in, keyword_ids=keyword_ids)
    return news


@router.get("/{news_id}", response_model=News)
async def read_news_item(
    *,
    db: AsyncSession = Depends(get_db),
    news_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定新闻
    """
    news = await get_news(db, news_id=news_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在",
        )
    return news


@router.put("/{news_id}", response_model=News)
async def update_news_item(
    *,
    db: AsyncSession = Depends(get_db),
    news_id: UUID,
    news_in: NewsUpdate,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    更新新闻（仅限管理员）
    """
    news = await get_news(db, news_id=news_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在",
        )
    news = await update_news(db, db_obj=news, obj_in=news_in)
    return news


@router.delete("/{news_id}", response_model=News)
async def delete_news_item(
    *,
    db: AsyncSession = Depends(get_db),
    news_id: UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    删除新闻（仅限管理员）
    """
    news = await get_news(db, news_id=news_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在",
        )
    news = await delete_news(db, news_id=news_id)
    return news


@router.post("/{news_id}/keywords/{keyword_id}", response_model=News)
async def add_keyword_to_news_item(
    *,
    db: AsyncSession = Depends(get_db),
    news_id: UUID,
    keyword_id: UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    为新闻添加关键词（仅限管理员）
    """
    news = await add_keyword_to_news(db, news_id=news_id, keyword_id=keyword_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻或关键词不存在",
        )
    return news


@router.delete("/{news_id}/keywords/{keyword_id}", response_model=News)
async def remove_keyword_from_news_item(
    *,
    db: AsyncSession = Depends(get_db),
    news_id: UUID,
    keyword_id: UUID,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    从新闻中移除关键词（仅限管理员）
    """
    news = await get_news(db, news_id=news_id)
    if not news:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="新闻不存在",
        )
    news = await remove_keyword_from_news(db, news_id=news_id, keyword_id=keyword_id)
    return news 