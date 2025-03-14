from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_current_active_user, get_current_active_superuser
from app.db.session import get_db
from app.models.user import User
from app.workers.tasks.crawl import crawl_news
from app.services.keyword import get_keyword

router = APIRouter()


@router.post("/crawl", response_model=Dict[str, Any])
async def start_crawl_task(
    *,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    keyword_id: UUID,
    source: str = "baidu",
    max_pages: int = 3,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    启动爬虫任务
    """
    # 检查关键词是否存在
    keyword = await get_keyword(db, keyword_id=keyword_id)
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="关键词不存在",
        )
    
    # 检查关键词是否属于当前用户
    if keyword.user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有足够的权限",
        )
    
    # 启动爬虫任务
    task = crawl_news.delay(keyword.text, source, max_pages)
    
    return {
        "task_id": task.id,
        "status": "started",
        "message": f"已启动爬虫任务，关键词: {keyword.text}, 来源: {source}",
    }


@router.get("/status/{task_id}", response_model=Dict[str, Any])
async def get_task_status(
    *,
    task_id: str,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    获取任务状态
    """
    # 从Celery获取任务状态
    task_result = crawl_news.AsyncResult(task_id)
    
    response = {
        "task_id": task_id,
        "status": task_result.status,
    }
    
    # 如果任务成功完成，返回结果
    if task_result.successful():
        response["result"] = task_result.result
    
    # 如果任务失败，返回错误信息
    if task_result.failed():
        response["error"] = str(task_result.result)
    
    return response


@router.delete("/revoke/{task_id}", response_model=Dict[str, Any])
async def revoke_task(
    *,
    task_id: str,
    terminate: bool = False,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    撤销任务（仅限管理员）
    """
    # 从Celery撤销任务
    crawl_news.AsyncResult(task_id).revoke(terminate=terminate)
    
    return {
        "task_id": task_id,
        "status": "revoked",
        "message": "任务已撤销",
    }


@router.post("/crawl_all", response_model=Dict[str, Any])
async def start_crawl_all_tasks(
    *,
    db: AsyncSession = Depends(get_db),
    source: str = "baidu",
    max_pages: int = 3,
    current_user: User = Depends(get_current_active_superuser),
) -> Any:
    """
    启动所有关键词的爬虫任务（仅限管理员）
    """
    # 这里应该从数据库获取所有活跃的关键词
    # 暂时返回一个示例响应
    return {
        "status": "started",
        "message": "已启动所有关键词的爬虫任务",
        "task_count": 0,
    } 