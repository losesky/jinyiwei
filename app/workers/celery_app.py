import os
from celery import Celery
from celery.signals import task_prerun, task_postrun, task_failure, worker_ready
from datetime import datetime
import time
import logging
import socket
import uuid

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 生成唯一的应用程序ID
hostname = socket.gethostname()
unique_id = str(uuid.uuid4())[:8]
app_name = f"jinyiwei-{hostname}-{unique_id}"

# 创建Celery实例
celery_app = Celery(
    app_name,
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.crawl",
        "app.workers.tasks.analysis",
        "app.workers.tasks.notification",
    ],
)

# 配置Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Shanghai",
    enable_utc=True,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_track_started=True,
    task_time_limit=3600,  # 1小时
    task_soft_time_limit=3000,  # 50分钟
    worker_max_tasks_per_child=200,
    worker_max_memory_per_child=200000,  # 200MB
    task_default_queue="default",
    broker_connection_retry=True,  # 连接重试
    broker_connection_retry_on_startup=True,  # 启动时连接重试（解决警告）
    broker_connection_max_retries=10,  # 最大重试次数
    worker_concurrency=1,  # 设置为1，避免多进程问题
    worker_proc_alive_timeout=60.0,  # 增加进程超时时间，避免进程检测问题
    worker_cancel_long_running_tasks_on_connection_loss=True,  # 连接丢失时取消长时间运行的任务
    worker_hijack_root_logger=False,  # 避免Celery接管根日志记录器
    beat_scheduler='celery.beat.PersistentScheduler',  # 使用持久化调度器
    beat_max_loop_interval=300,  # 最大循环间隔（秒）
    beat_sync_every=1,  # 每次循环都同步到磁盘
    worker_disable_rate_limits=True,  # 禁用速率限制
    event_queue_expires=60,  # 事件队列过期时间（秒）
    event_queue_ttl=10,  # 事件队列生存时间（秒）
    worker_send_task_events=False,  # 禁用任务事件发送
    worker_enable_remote_control=False,  # 禁用远程控制
    task_queues={
        "high": {"exchange": "high", "routing_key": "high"},
        "default": {"exchange": "default", "routing_key": "default"},
        "low": {"exchange": "low", "routing_key": "low"},
    },
    task_routes={
        "app.workers.tasks.crawl.*": {"queue": "high"},
        "app.workers.tasks.analysis.*": {"queue": "default"},
        "app.workers.tasks.notification.*": {"queue": "low"},
    },
)


# 任务基类，用于监控任务执行
class MonitoredTask(celery_app.Task):
    """
    带监控功能的任务基类
    """
    abstract = True
    
    def __call__(self, *args, **kwargs):
        """
        执行任务并记录性能指标
        """
        self.start_time = time.time()
        return super().__call__(*args, **kwargs)
    
    def on_success(self, retval, task_id, args, kwargs):
        """
        任务成功完成时的回调
        """
        execution_time = time.time() - self.start_time
        logger.info(
            f"Task {self.name}[{task_id}] succeeded in {execution_time:.2f}s"
        )
        # 这里可以添加将任务执行信息保存到数据库的代码
        super().on_success(retval, task_id, args, kwargs)
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """
        任务失败时的回调
        """
        execution_time = time.time() - self.start_time
        logger.error(
            f"Task {self.name}[{task_id}] failed in {execution_time:.2f}s: {exc}"
        )
        # 这里可以添加将任务失败信息保存到数据库的代码
        super().on_failure(exc, task_id, args, kwargs, einfo)


# 任务信号处理
@task_prerun.connect
def task_prerun_handler(task_id, task, args, kwargs, **kw):
    """
    任务开始前的处理
    """
    logger.info(f"Task {task.name}[{task_id}] started")


@task_postrun.connect
def task_postrun_handler(task_id, task, args, kwargs, retval, state, **kw):
    """
    任务完成后的处理
    """
    logger.info(f"Task {task.name}[{task_id}] finished with state {state}")


@task_failure.connect
def task_failure_handler(task_id, exception, args, kwargs, traceback, einfo, **kw):
    """
    任务失败的处理
    """
    logger.error(f"Task {task_id} failed: {exception}")


@worker_ready.connect
def worker_ready_handler(**kwargs):
    """
    Worker就绪的处理
    """
    logger.info("Celery worker is ready") 