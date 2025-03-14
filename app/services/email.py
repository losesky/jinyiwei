import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Optional

from app.core.config import settings

logger = logging.getLogger(__name__)


async def send_email(
    email_to: str,
    subject: str,
    html_content: str,
    cc: Optional[List[str]] = None,
) -> bool:
    """
    发送电子邮件
    """
    if not settings.SMTP_HOST or not settings.SMTP_PORT:
        logger.warning("SMTP配置不完整，无法发送邮件")
        return False
    
    message = MIMEMultipart()
    message["From"] = settings.EMAILS_FROM_EMAIL
    message["To"] = email_to
    message["Subject"] = subject
    
    if cc:
        message["Cc"] = ", ".join(cc)
    
    message.attach(MIMEText(html_content, "html"))
    
    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            if settings.SMTP_TLS:
                server.starttls()
            if settings.SMTP_USER and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            
            recipients = [email_to]
            if cc:
                recipients.extend(cc)
            
            server.sendmail(settings.EMAILS_FROM_EMAIL, recipients, message.as_string())
        
        logger.info(f"邮件已发送至 {email_to}")
        return True
    except Exception as e:
        logger.error(f"发送邮件失败: {e}")
        return False


async def send_reset_password_email(
    email_to: str,
    username: str,
    reset_url: str,
) -> bool:
    """
    发送密码重置邮件
    """
    subject = f"{settings.PROJECT_NAME} - 密码重置"
    
    html_content = f"""
    <html>
    <body>
        <p>您好 {username},</p>
        <p>您收到此邮件是因为您请求重置您在 {settings.PROJECT_NAME} 的密码。</p>
        <p>请点击以下链接重置您的密码:</p>
        <p><a href="{reset_url}">{reset_url}</a></p>
        <p>此链接将在24小时后失效。</p>
        <p>如果您没有请求重置密码，请忽略此邮件。</p>
        <p>谢谢,</p>
        <p>{settings.PROJECT_NAME} 团队</p>
    </body>
    </html>
    """
    
    return await send_email(
        email_to=email_to,
        subject=subject,
        html_content=html_content,
    ) 