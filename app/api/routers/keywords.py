from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.keyword import Keyword, KeywordCreate, KeywordUpdate
from app.services.keyword import (
    create_keyword,
    delete_keyword,
    get_keyword,
    get_keywords,
    update_keyword,
)

router = APIRouter()


@router.get("/", response_model=List[Keyword])
async def read_keywords(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取关键词列表
    """
    keywords = await get_keywords(db, user_id=current_user.id, skip=skip, limit=limit)
    return keywords


@router.post("/", response_model=Keyword)
async def create_new_keyword(
    *,
    db: AsyncSession = Depends(get_db),
    keyword_in: KeywordCreate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    创建新关键词
    """
    keyword = await create_keyword(db, keyword_in=keyword_in, user_id=current_user.id)
    return keyword


@router.get("/{keyword_id}", response_model=Keyword)
async def read_keyword(
    *,
    db: AsyncSession = Depends(get_db),
    keyword_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取指定关键词
    """
    keyword = await get_keyword(db, keyword_id=keyword_id)
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在",
        )
    if keyword.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    return keyword


@router.put("/{keyword_id}", response_model=Keyword)
async def update_existing_keyword(
    *,
    db: AsyncSession = Depends(get_db),
    keyword_id: UUID,
    keyword_in: KeywordUpdate,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    更新关键词
    """
    keyword = await get_keyword(db, keyword_id=keyword_id)
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在",
        )
    if keyword.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    keyword = await update_keyword(db, db_obj=keyword, obj_in=keyword_in)
    return keyword


@router.delete("/{keyword_id}", response_model=Keyword)
async def delete_existing_keyword(
    *,
    db: AsyncSession = Depends(get_db),
    keyword_id: UUID,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    删除关键词
    """
    keyword = await get_keyword(db, keyword_id=keyword_id)
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在",
        )
    if keyword.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    keyword = await delete_keyword(db, keyword_id=keyword_id)
    return keyword 