import asyncio
import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import engine

logger = logging.getLogger(__name__)


async def migrate_db() -> None:
    """
    迁移数据库
    """
    try:
        # 执行SQL语句重命名表
        async with engine.begin() as conn:
            # 检查users表是否已存在
            result = await conn.execute(text("SELECT to_regclass('users');"))
            users_exists = result.scalar()
            
            if not users_exists:
                # 检查user表是否存在
                result = await conn.execute(text("SELECT to_regclass('\"user\"');"))
                user_exists = result.scalar()
                
                if user_exists:
                    # 重命名表
                    await conn.execute(text('ALTER TABLE "user" RENAME TO users;'))
                    logger.info("表 'user' 已重命名为 'users'")
                else:
                    logger.warning("表 'user' 不存在，无法重命名")
            else:
                logger.info("表 'users' 已存在，无需重命名")
        
        logger.info("数据库迁移成功")
        
    except Exception as e:
        logger.error(f"数据库迁移失败: {e}")
        raise


if __name__ == "__main__":
    """
    直接运行此脚本迁移数据库
    """
    asyncio.run(migrate_db()) 