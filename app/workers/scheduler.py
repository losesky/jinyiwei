import logging
from typing import Dict, List, Optional
import asyncio
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.workers.tasks.crawl import crawl_news
from app.workers.tasks.notification import send_daily_digest
from app.db.session import AsyncSessionLocal
from app.services.keyword import get_keywords

logger = logging.getLogger(__name__)

# 创建调度器
jobstores = {
    'default': SQLAlchemyJobStore(url=str(settings.DATABASE_URL).replace('+asyncpg', ''))
}

executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}

job_defaults = {
    'coalesce': False,
    'max_instances': 3
}

scheduler = AsyncIOScheduler(
    jobstores=jobstores,
    executors=executors,
    job_defaults=job_defaults,
    timezone='Asia/Shanghai'
)


async def crawl_all_keywords(source: str = "baidu", max_pages: int = 3) -> None:
    """
    抓取所有活跃关键词的新闻
    """
    logger.info(f"开始抓取所有关键词的新闻，来源: {source}")
    
    try:
        # 获取所有活跃的关键词
        async with AsyncSessionLocal() as db:
            keywords = await get_keywords(db, user_id=None, is_active=True)
        
        # 为每个关键词启动爬虫任务
        for keyword in keywords:
            crawl_news.delay(keyword.text, source, max_pages)
            logger.info(f"已启动关键词 '{keyword.text}' 的爬虫任务")
        
        logger.info(f"成功启动 {len(keywords)} 个关键词的爬虫任务")
    
    except Exception as e:
        logger.error(f"抓取所有关键词的新闻失败: {str(e)}")


async def send_daily_digests() -> None:
    """
    发送每日新闻摘要
    """
    logger.info("开始发送每日新闻摘要")
    
    try:
        # 这里应该从数据库获取所有用户和他们的新闻
        # 暂时省略实现
        logger.info("每日新闻摘要发送完成")
    
    except Exception as e:
        logger.error(f"发送每日新闻摘要失败: {str(e)}")


def setup_scheduler() -> None:
    """
    设置定时任务
    """
    # 每小时抓取一次所有关键词的新闻
    scheduler.add_job(
        crawl_all_keywords,
        'interval',
        hours=1,
        id='crawl_all_keywords',
        replace_existing=True,
        args=["baidu", 3]
    )
    
    # 每天早上9点发送每日新闻摘要
    scheduler.add_job(
        send_daily_digests,
        'cron',
        hour=9,
        minute=0,
        id='send_daily_digests',
        replace_existing=True
    )
    
    # 启动调度器
    scheduler.start()
    logger.info("任务调度器已启动") 