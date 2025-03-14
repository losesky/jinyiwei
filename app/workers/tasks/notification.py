import logging
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2
from datetime import datetime

from app.workers.celery_app import celery_app, MonitoredTask
from app.core.config import settings

logger = logging.getLogger(__name__)

# 初始化Jinja2模板环境
template_loader = jinja2.FileSystemLoader(searchpath="app/templates")
template_env = jinja2.Environment(loader=template_loader)


@celery_app.task(
    bind=True,
    base=MonitoredTask,
    max_retries=3,
    retry_backoff=True,
)
def send_news_notification(self, news_item: Dict, recipients: Optional[List[str]] = None) -> bool:
    """
    发送新闻通知邮件
    
    Args:
        news_item: 新闻数据
        recipients: 收件人列表，如果为None则使用默认收件人
    
    Returns:
        是否发送成功
    """
    logger.info(f"准备发送新闻通知: {news_item.get('title', '无标题')}")
    
    try:
        # 如果没有指定收件人，则使用默认收件人（这里应该从数据库获取）
        if not recipients:
            # 这里应该从数据库获取订阅了该关键词的用户邮箱
            # 暂时使用配置中的默认发件人作为测试
            recipients = [settings.MAIL_FROM]
        
        # 准备邮件内容
        subject = f"新闻提醒: {news_item.get('title', '无标题')}"
        
        # 使用模板渲染邮件内容
        try:
            template = template_env.get_template("news_notification.html")
            html_content = template.render(
                title=news_item.get('title', '无标题'),
                content=news_item.get('content', ''),
                summary=news_item.get('summary', ''),
                url=news_item.get('url', ''),
                source=news_item.get('source', '未知来源'),
                published_at=news_item.get('published_at', datetime.now()).strftime('%Y-%m-%d %H:%M:%S'),
                sentiment_score=news_item.get('sentiment_score', 0),
            )
        except Exception as e:
            logger.error(f"渲染邮件模板失败: {str(e)}")
            # 使用简单文本作为备用
            html_content = f"""
            <h1>{news_item.get('title', '无标题')}</h1>
            <p><strong>来源:</strong> {news_item.get('source', '未知来源')}</p>
            <p><strong>发布时间:</strong> {news_item.get('published_at', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p><strong>情感分数:</strong> {news_item.get('sentiment_score', 0)}</p>
            <p><strong>摘要:</strong> {news_item.get('summary', news_item.get('content', '无内容'))}</p>
            <p><a href="{news_item.get('url', '#')}">阅读原文</a></p>
            """
        
        # 发送邮件
        success = send_email(recipients, subject, html_content)
        
        if success:
            logger.info(f"成功发送新闻通知: {news_item.get('title', '无标题')}")
        else:
            logger.error(f"发送新闻通知失败: {news_item.get('title', '无标题')}")
            self.retry(countdown=60 * (self.request.retries + 1))
        
        return success
    
    except Exception as e:
        logger.error(f"发送新闻通知失败: {str(e)}")
        self.retry(exc=e, countdown=60 * (self.request.retries + 1))


def send_email(recipients: List[str], subject: str, html_content: str) -> bool:
    """
    发送邮件
    
    Args:
        recipients: 收件人列表
        subject: 邮件主题
        html_content: HTML格式的邮件内容
    
    Returns:
        是否发送成功
    """
    try:
        # 创建邮件
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.MAIL_FROM}>"
        message["To"] = ", ".join(recipients)
        
        # 添加HTML内容
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # 连接SMTP服务器并发送
        with smtplib.SMTP(settings.MAIL_SERVER, settings.MAIL_PORT) as server:
            if settings.MAIL_TLS:
                server.starttls()
            
            if settings.MAIL_USERNAME and settings.MAIL_PASSWORD:
                server.login(settings.MAIL_USERNAME, settings.MAIL_PASSWORD)
            
            server.sendmail(settings.MAIL_FROM, recipients, message.as_string())
        
        return True
    
    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}")
        return False


@celery_app.task(
    bind=True,
    base=MonitoredTask,
)
def send_daily_digest(self, user_id: str, news_items: List[Dict]) -> bool:
    """
    发送每日新闻摘要
    
    Args:
        user_id: 用户ID
        news_items: 新闻列表
    
    Returns:
        是否发送成功
    """
    logger.info(f"准备发送每日新闻摘要给用户 {user_id}")
    
    try:
        # 这里应该从数据库获取用户信息和邮箱
        # 暂时使用配置中的默认发件人作为测试
        recipient = settings.MAIL_FROM
        
        # 准备邮件内容
        subject = f"每日新闻摘要 - {datetime.now().strftime('%Y-%m-%d')}"
        
        # 使用模板渲染邮件内容
        try:
            template = template_env.get_template("daily_digest.html")
            html_content = template.render(
                date=datetime.now().strftime('%Y-%m-%d'),
                news_items=news_items,
            )
        except Exception as e:
            logger.error(f"渲染邮件模板失败: {str(e)}")
            # 使用简单文本作为备用
            html_content = f"""
            <h1>每日新闻摘要 - {datetime.now().strftime('%Y-%m-%d')}</h1>
            """
            for item in news_items:
                html_content += f"""
                <div>
                    <h2>{item.get('title', '无标题')}</h2>
                    <p><strong>来源:</strong> {item.get('source', '未知来源')}</p>
                    <p><strong>发布时间:</strong> {item.get('published_at', datetime.now()).strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p><strong>摘要:</strong> {item.get('summary', item.get('content', '无内容'))}</p>
                    <p><a href="{item.get('url', '#')}">阅读原文</a></p>
                </div>
                <hr>
                """
        
        # 发送邮件
        success = send_email([recipient], subject, html_content)
        
        if success:
            logger.info(f"成功发送每日新闻摘要给用户 {user_id}")
        else:
            logger.error(f"发送每日新闻摘要失败: 用户 {user_id}")
        
        return success
    
    except Exception as e:
        logger.error(f"发送每日新闻摘要失败: {str(e)}")
        return False 