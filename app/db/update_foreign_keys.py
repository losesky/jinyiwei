import asyncio
import logging
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import engine

logger = logging.getLogger(__name__)


async def update_foreign_keys() -> None:
    """
    更新外键引用
    """
    try:
        # 执行SQL语句更新外键
        async with engine.begin() as conn:
            # 检查keyword表是否存在
            result = await conn.execute(text("SELECT to_regclass('keyword');"))
            keyword_exists = result.scalar()
            
            if keyword_exists:
                # 检查外键约束
                result = await conn.execute(text("""
                    SELECT conname FROM pg_constraint 
                    WHERE conrelid = 'keyword'::regclass 
                    AND contype = 'f' 
                    AND confrelid = 'user'::regclass;
                """))
                fk_constraints = result.fetchall()
                
                # 删除旧的外键约束
                for constraint in fk_constraints:
                    await conn.execute(text(f'ALTER TABLE keyword DROP CONSTRAINT {constraint[0]};'))
                    logger.info(f"删除了外键约束: {constraint[0]}")
                
                # 添加新的外键约束
                await conn.execute(text("""
                    ALTER TABLE keyword 
                    ADD CONSTRAINT keyword_user_id_fkey 
                    FOREIGN KEY (user_id) REFERENCES users(id);
                """))
                logger.info("添加了新的外键约束: keyword_user_id_fkey")
            
            # 检查task表是否存在
            result = await conn.execute(text("SELECT to_regclass('task');"))
            task_exists = result.scalar()
            
            if task_exists:
                # 检查外键约束
                result = await conn.execute(text("""
                    SELECT conname FROM pg_constraint 
                    WHERE conrelid = 'task'::regclass 
                    AND contype = 'f' 
                    AND confrelid = 'user'::regclass;
                """))
                fk_constraints = result.fetchall()
                
                # 删除旧的外键约束
                for constraint in fk_constraints:
                    await conn.execute(text(f'ALTER TABLE task DROP CONSTRAINT {constraint[0]};'))
                    logger.info(f"删除了外键约束: {constraint[0]}")
                
                # 添加新的外键约束
                await conn.execute(text("""
                    ALTER TABLE task 
                    ADD CONSTRAINT task_user_id_fkey 
                    FOREIGN KEY (user_id) REFERENCES users(id);
                """))
                logger.info("添加了新的外键约束: task_user_id_fkey")
        
        logger.info("外键更新成功")
        
    except Exception as e:
        logger.error(f"外键更新失败: {e}")
        raise


if __name__ == "__main__":
    """
    直接运行此脚本更新外键
    """
    asyncio.run(update_foreign_keys()) 