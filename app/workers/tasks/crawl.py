import logging
from typing import Dict, List, Optional
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import random

from app.workers.celery_app import celery_app, MonitoredTask
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(
    bind=True,
    base=MonitoredTask,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def crawl_news(
    self,
    keyword: str,
    source: str = "baidu",
    max_pages: int = 3,
    proxy: Optional[str] = None,
) -> List[Dict]:
    """
    抓取新闻任务
    
    Args:
        keyword: 要搜索的关键词
        source: 数据源 (baidu, google, bing, sogou)
        max_pages: 最大抓取页数
        proxy: 代理服务器地址
    
    Returns:
        抓取到的新闻列表
    """
    logger.info(f"开始抓取关键词 '{keyword}' 的新闻，来源: {source}")
    
    try:
        if source == "baidu":
            news_items = _crawl_baidu_news(keyword, max_pages, proxy)
        elif source == "google":
            news_items = _crawl_google_news(keyword, max_pages, proxy)
        else:
            logger.error(f"不支持的数据源: {source}")
            return []
        
        logger.info(f"成功抓取 {len(news_items)} 条关于 '{keyword}' 的新闻")
        
        # 触发数据处理任务
        from app.workers.tasks.analysis import process_news
        for news_item in news_items:
            process_news.delay(news_item)
        
        return news_items
    
    except Exception as e:
        logger.error(f"抓取新闻失败: {str(e)}")
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


def _crawl_baidu_news(keyword: str, max_pages: int = 3, proxy: Optional[str] = None) -> List[Dict]:
    """
    从百度新闻抓取数据
    """
    news_items = []
    headers = {
        "User-Agent": settings.USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3",
    }
    
    proxies = {"http": proxy, "https": proxy} if proxy else None
    
    for page in range(max_pages):
        try:
            url = f"https://news.baidu.com/ns?word={keyword}&pn={page * 10}&cl=2&ct=1&tn=news&rn=10&ie=utf-8&bt=0&et=0"
            
            # 添加随机延迟，避免被封
            time.sleep(settings.CRAWL_DELAY + random.uniform(0, 2))
            
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, "html.parser")
            news_divs = soup.select("div.result")
            
            for div in news_divs:
                try:
                    title_elem = div.select_one("h3 a")
                    if not title_elem:
                        continue
                    
                    title = title_elem.text.strip()
                    news_url = title_elem["href"]
                    
                    content_elem = div.select_one("div.c-summary")
                    content = content_elem.text.strip() if content_elem else ""
                    
                    source_time = div.select_one("div.c-author")
                    source = ""
                    published_at = None
                    
                    if source_time:
                        source_text = source_time.text.strip()
                        parts = source_text.split()
                        if len(parts) >= 2:
                            source = parts[0]
                            try:
                                time_str = parts[1].replace("年", "-").replace("月", "-").replace("日", "")
                                published_at = datetime.strptime(time_str, "%Y-%m-%d")
                            except:
                                pass
                    
                    news_items.append({
                        "title": title,
                        "url": news_url,
                        "content": content,
                        "source": source or "百度新闻",
                        "published_at": published_at,
                        "crawled_at": datetime.utcnow(),
                    })
                
                except Exception as e:
                    logger.warning(f"解析新闻项失败: {str(e)}")
                    continue
        
        except Exception as e:
            logger.error(f"抓取百度新闻第 {page + 1} 页失败: {str(e)}")
            continue
    
    return news_items


def _crawl_google_news(keyword: str, max_pages: int = 3, proxy: Optional[str] = None) -> List[Dict]:
    """
    从Google新闻抓取数据
    """
    # 实际实现中需要处理Google新闻的抓取逻辑
    # 这里只是一个示例框架
    logger.info(f"Google新闻抓取功能尚未实现")
    return [] 