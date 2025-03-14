import asyncio
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import engine
from app.db.base import Base
from app.schemas.user import UserCreate
from app.services.user import create_user, get_user_by_username

logger = logging.getLogger(__name__)


async def init_db(db: AsyncSession) -> None:
    """
    初始化数据库
    """
    try:
        # 创建所有表
        async with engine.begin() as conn:
            # 删除所有表（仅在开发环境使用）
            # await conn.run_sync(Base.metadata.drop_all)
            
            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("数据库表创建成功")
        
        # 创建超级用户
        await create_admin_user(db)
        
    except Exception as e:
        logger.error(f"初始化数据库失败: {e}")
        raise


async def create_admin_user(db: AsyncSession) -> None:
    """
    创建超级管理员用户
    """
    try:
        # 检查管理员用户是否已存在
        admin_user = await get_user_by_username(db, username=settings.FIRST_SUPERUSER)
        
        if not admin_user:
            # 创建管理员用户
            user_in = UserCreate(
                username=settings.FIRST_SUPERUSER,
                email=settings.FIRST_SUPERUSER_EMAIL,
                password=settings.FIRST_SUPERUSER_PASSWORD,
                is_superuser=True,
            )
            
            admin_user = await create_user(db, user_in=user_in)
            logger.info(f"超级管理员用户 {admin_user.username} 创建成功")
        else:
            logger.info(f"超级管理员用户 {admin_user.username} 已存在")
            
    except Exception as e:
        logger.error(f"创建超级管理员用户失败: {e}")
        raise


if __name__ == "__main__":
    """
    直接运行此脚本初始化数据库
    """
    from app.db.session import get_db
    
    async def init() -> None:
        async for db in get_db():
            await init_db(db)
    
    asyncio.run(init()) 