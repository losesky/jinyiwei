from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.api.routers import auth, keywords, news, tasks, users
from app.core.config import settings
from app.core.security import get_current_active_user
from app.workers.scheduler import setup_scheduler

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
)

# Set up CORS
logger.info("Setting up CORS middleware")
logger.info(f"CORS origins: {settings.FRONTEND_URL}")
logger.info(f"CORS credentials: False")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # 允许本地两种不同的访问方式
    allow_credentials=False,  # 与前端 withCredentials: false 保持一致
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["Content-Type", "Authorization"],
)

logger.info("CORS middleware configured successfully")

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/auth",
    tags=["认证"],
)

app.include_router(
    users.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["用户"],
    dependencies=[Depends(get_current_active_user)],
)

app.include_router(
    keywords.router,
    prefix=f"{settings.API_V1_STR}/keywords",
    tags=["关键词"],
    dependencies=[Depends(get_current_active_user)],
)

app.include_router(
    news.router,
    prefix=f"{settings.API_V1_STR}/news",
    tags=["新闻"],
    dependencies=[Depends(get_current_active_user)],
)

app.include_router(
    tasks.router,
    prefix=f"{settings.API_V1_STR}/tasks",
    tags=["任务"],
    dependencies=[Depends(get_current_active_user)],
)

@app.get("/", tags=["健康检查"])
async def health_check():
    """
    健康检查端点
    """
    return JSONResponse(
        status_code=200,
        content={"status": "ok", "message": "服务正常运行"}
    )


@app.on_event("startup")
async def startup_event():
    """
    应用启动时的事件处理
    """
    logger.info("应用启动")
    
    # 启动任务调度器
    try:
        setup_scheduler()
        logger.info("任务调度器已启动")
    except Exception as e:
        logger.error(f"启动任务调度器失败: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """
    应用关闭时的事件处理
    """
    logger.info("应用关闭")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 