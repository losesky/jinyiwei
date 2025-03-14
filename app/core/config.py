import os
import secrets
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, PostgresDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=True)

    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "锦衣卫"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ALGORITHM: str = "HS256"
    
    # 环境设置
    ENV: str = "development"  # 可选值: development, production, testing

    # CORS
    CORS_ORIGINS: List[AnyHttpUrl] = []

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> Union[List[str], str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Frontend
    FRONTEND_URL: str = "http://localhost:3000"

    # Database
    DATABASE_URL: PostgresDsn
    TEST_DATABASE_URL: Optional[PostgresDsn] = None

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    # Email
    SMTP_TLS: bool = True
    SMTP_PORT: int = 587
    SMTP_HOST: str = "smtp.qq.com"
    SMTP_USER: str = "example@example.com"
    SMTP_PASSWORD: str = ""
    EMAILS_FROM_EMAIL: str = "example@example.com"
    EMAILS_FROM_NAME: str = "锦衣卫系统"
    EMAIL_TEMPLATES_DIR: str = "app/templates/email"
    EMAIL_TEST_USER: str = "test@example.com"
    MAIL_TLS: bool = True
    MAIL_SSL: bool = False

    # 初始超级用户
    FIRST_SUPERUSER: str = "admin"
    FIRST_SUPERUSER_EMAIL: str = "admin@example.com"
    FIRST_SUPERUSER_PASSWORD: str = "Admin123"

    # Crawler
    PROXY_ENABLED: bool = False
    PROXY_API_URL: Optional[str] = None
    PROXY_API_KEY: Optional[str] = None
    CRAWL_DELAY: int = 2
    USER_AGENT: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    # Monitoring
    SENTRY_DSN: Optional[str] = None
    ENABLE_PROMETHEUS: bool = True
    PROMETHEUS_PORT: int = 9090

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"


settings = Settings() 