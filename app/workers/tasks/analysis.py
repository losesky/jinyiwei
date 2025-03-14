import logging
from typing import Dict, Optional
import re
from datetime import datetime
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import time
import os

from app.workers.celery_app import celery_app, MonitoredTask
from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 设置NLTK数据目录为项目数据目录
nltk_data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), "data/nltk_data")
os.makedirs(nltk_data_dir, exist_ok=True)
nltk.data.path.insert(0, nltk_data_dir)

# 初始化NLTK资源
def download_nltk_data(resource, dir=nltk_data_dir):
    """安全地下载NLTK资源"""
    try:
        nltk.data.find(resource)
        logger.info(f"NLTK资源 {resource} 已存在")
    except LookupError:
        try:
            logger.info(f"正在下载NLTK资源 {resource} 到 {dir}")
            nltk.download(resource.split('/')[-1], download_dir=dir, quiet=False)
            logger.info(f"NLTK资源 {resource} 下载完成")
        except Exception as e:
            logger.error(f"下载NLTK资源 {resource} 失败: {e}")
            # 尝试使用系统默认位置
            try:
                logger.info(f"尝试使用系统默认位置下载NLTK资源 {resource}")
                nltk.download(resource.split('/')[-1], quiet=False)
            except Exception as e2:
                logger.error(f"使用系统默认位置下载NLTK资源 {resource} 也失败: {e2}")

# 下载必要的NLTK资源
download_nltk_data('tokenizers/punkt')
download_nltk_data('sentiment/vader_lexicon.zip')

@celery_app.task(
    bind=True,
    base=MonitoredTask,
    max_retries=2,
    retry_backoff=True,
)
def process_news(self, news_item: Dict) -> Dict:
    """
    处理新闻数据任务
    
    Args:
        news_item: 新闻数据字典
    
    Returns:
        处理后的新闻数据
    """
    logger.info(f"开始处理新闻: {news_item.get('title', '无标题')}")
    
    try:
        # 1. 文本清洗
        news_item = clean_text(news_item)
        
        # 2. 数据验证
        if not validate_news(news_item):
            logger.warning(f"新闻数据验证失败: {news_item.get('title', '无标题')}")
            return news_item
        
        # 3. 情感分析
        news_item = analyze_sentiment(news_item)
        
        # 4. 生成摘要
        news_item = generate_summary(news_item)
        
        # 5. 保存到数据库
        # 这里应该调用数据库服务保存数据
        # 暂时省略实现
        
        # 6. 触发通知任务
        from app.workers.tasks.notification import send_news_notification
        if news_item.get('sentiment_score', 0) < -0.5:  # 负面新闻通知
            send_news_notification.delay(news_item)
        
        logger.info(f"成功处理新闻: {news_item.get('title', '无标题')}")
        return news_item
    
    except Exception as e:
        logger.error(f"处理新闻失败: {str(e)}")
        self.retry(exc=e, countdown=60)


def clean_text(news_item: Dict) -> Dict:
    """
    清洗文本数据
    """
    # 复制一份，避免修改原始数据
    cleaned_item = news_item.copy()
    
    # 清洗标题
    if 'title' in cleaned_item and cleaned_item['title']:
        # 去除HTML标签
        cleaned_item['title'] = re.sub(r'<[^>]+>', '', cleaned_item['title'])
        # 去除多余空白
        cleaned_item['title'] = re.sub(r'\s+', ' ', cleaned_item['title']).strip()
    
    # 清洗内容
    if 'content' in cleaned_item and cleaned_item['content']:
        # 去除HTML标签
        cleaned_item['content'] = re.sub(r'<[^>]+>', '', cleaned_item['content'])
        # 去除多余空白
        cleaned_item['content'] = re.sub(r'\s+', ' ', cleaned_item['content']).strip()
        # 去除特殊字符
        cleaned_item['content'] = re.sub(r'[^\w\s.,;:!?，。；：！？]', '', cleaned_item['content'])
    
    return cleaned_item


def validate_news(news_item: Dict) -> bool:
    """
    验证新闻数据
    """
    # 检查必填字段
    if not news_item.get('title') or not news_item.get('url'):
        return False
    
    # 检查URL格式
    url_pattern = re.compile(
        r'^(https?:\/\/)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
    )
    if not url_pattern.match(news_item.get('url', '')):
        return False
    
    # 检查日期格式
    if 'published_at' in news_item and news_item['published_at']:
        if not isinstance(news_item['published_at'], datetime):
            try:
                # 尝试转换为datetime
                if isinstance(news_item['published_at'], str):
                    datetime.fromisoformat(news_item['published_at'].replace('Z', '+00:00'))
            except ValueError:
                return False
    
    return True


def analyze_sentiment(news_item: Dict) -> Dict:
    """
    分析新闻情感
    """
    # 复制一份，避免修改原始数据
    analyzed_item = news_item.copy()
    
    # 初始化情感分析器
    sid = SentimentIntensityAnalyzer()
    
    # 分析标题情感
    title_sentiment = 0
    if 'title' in analyzed_item and analyzed_item['title']:
        title_sentiment = sid.polarity_scores(analyzed_item['title'])['compound']
    
    # 分析内容情感
    content_sentiment = 0
    if 'content' in analyzed_item and analyzed_item['content']:
        content_sentiment = sid.polarity_scores(analyzed_item['content'])['compound']
    
    # 综合情感分数 (标题权重0.4，内容权重0.6)
    if 'title' in analyzed_item and 'content' in analyzed_item:
        analyzed_item['sentiment_score'] = title_sentiment * 0.4 + content_sentiment * 0.6
    elif 'title' in analyzed_item:
        analyzed_item['sentiment_score'] = title_sentiment
    elif 'content' in analyzed_item:
        analyzed_item['sentiment_score'] = content_sentiment
    else:
        analyzed_item['sentiment_score'] = 0
    
    return analyzed_item


def generate_summary(news_item: Dict) -> Dict:
    """
    生成新闻摘要
    """
    # 复制一份，避免修改原始数据
    summarized_item = news_item.copy()
    
    # 如果已有摘要或内容为空，则跳过
    if 'summary' in summarized_item and summarized_item['summary'] or not summarized_item.get('content'):
        return summarized_item
    
    content = summarized_item['content']
    
    # 简单的抽取式摘要：取前2-3个句子
    sentences = sent_tokenize(content)
    
    if len(sentences) <= 3:
        summarized_item['summary'] = content
    else:
        # 取前3个句子作为摘要
        summarized_item['summary'] = ' '.join(sentences[:3])
    
    return summarized_item 