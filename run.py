import uvicorn
import argparse
import logging
import os
import sys
import subprocess
import threading
import time
import getpass
import socket
from dotenv import load_dotenv
import uuid

# 加载环境变量
load_dotenv()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def is_port_in_use(port, host='0.0.0.0'):
    """
    检查端口是否被占用
    
    Args:
        port: 端口号
        host: 主机地址
        
    Returns:
        bool: 如果端口被占用返回True，否则返回False
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind((host, port))
            return False
        except socket.error:
            return True


def find_available_port(start_port, host='0.0.0.0'):
    """
    查找可用端口
    
    Args:
        start_port: 起始端口号
        host: 主机地址
        
    Returns:
        int: 可用的端口号
    """
    port = start_port
    while is_port_in_use(port, host):
        port += 1
        if port > 65535:
            raise RuntimeError("无法找到可用端口")
    return port


def get_uid_from_username(username):
    """
    根据用户名获取用户ID
    
    Args:
        username: 用户名
        
    Returns:
        int: 用户ID，如果找不到则返回None
    """
    try:
        import pwd
        return pwd.getpwnam(username).pw_uid
    except (KeyError, ImportError) as e:
        logger.error(f"无法获取用户 {username} 的ID: {e}")
        return None


def get_non_root_user():
    """
    获取非root用户ID
    
    Returns:
        int: 非root用户ID，如果找不到则返回None
    """
    try:
        # 尝试获取当前登录用户的ID
        username = os.environ.get('SUDO_USER') or os.environ.get('USER')
        if username and username != 'root':
            return get_uid_from_username(username)
    except Exception as e:
        logger.warning(f"无法获取非root用户ID: {e}")
    return None


def ensure_dir_exists(directory, mode=0o777):
    """
    确保目录存在，如果不存在则创建，并设置适当的权限
    
    Args:
        directory: 目录路径
        mode: 目录权限模式
    """
    # 检查目录是否存在
    if not os.path.exists(directory):
        try:
            os.makedirs(directory, mode=mode, exist_ok=True)
            logger.info(f"创建目录: {directory}")
        except Exception as e:
            logger.warning(f"无法创建目录: {e}")
            return False
    
    # 设置目录权限，确保所有用户可访问
    try:
        # 检查当前用户是否有权限修改该目录
        if os.access(directory, os.W_OK):
            os.chmod(directory, mode)
            logger.info(f"设置目录权限: {directory} (mode={oct(mode)})")
        else:
            # 如果没有权限，只记录一个调试信息，而不是警告
            logger.debug(f"无权限修改目录: {directory}")
    except Exception as e:
        # 如果设置权限失败，只记录一个调试信息，而不是警告
        logger.debug(f"无法设置目录权限: {e}")
    
    return True


def stop_celery_processes():
    """
    停止所有运行中的Celery进程
    """
    try:
        logger.info("尝试停止已有的Celery进程...")
        # 使用pkill命令停止所有Celery进程
        subprocess.run(
            ["pkill", "-f", "celery -A app.workers.celery_app"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False
        )
        # 等待进程完全停止
        time.sleep(2)
        logger.info("已停止所有Celery进程")
    except Exception as e:
        logger.warning(f"停止Celery进程时出错: {e}")


def run_celery_worker(uid=None):
    """
    启动Celery Worker
    
    Args:
        uid: 运行Celery Worker的用户ID，如果为None则使用当前用户
    """
    logger.info("启动Celery Worker")
    
    # 停止已有的Celery进程
    stop_celery_processes()
    
    # 设置NLTK数据目录环境变量
    nltk_data_dir = os.path.join(os.getcwd(), "data/nltk_data")
    os.environ["NLTK_DATA"] = nltk_data_dir
    logger.info(f"设置NLTK_DATA环境变量: {nltk_data_dir}")
    
    # 生成唯一的节点名称
    hostname = socket.gethostname()
    unique_id = str(uuid.uuid4())[:8]
    node_name = f"worker-{hostname}-{unique_id}"
    
    # 构建命令
    cmd = [
        "celery", 
        "-A", 
        "app.workers.celery_app", 
        "worker", 
        "--loglevel=info",
        "-P", 
        "solo",  # 使用solo池避免多进程问题
        "-n",
        node_name  # 使用唯一的节点名称
    ]
    
    # 如果指定了uid，添加--uid选项
    if uid is not None:
        cmd.extend(["--uid", str(uid)])
    
    # 最大重试次数
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 创建环境变量副本
            env = os.environ.copy()
            # 启动进程
            logger.info(f"执行命令: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, env=env)
            break  # 如果成功，跳出循环
        except subprocess.CalledProcessError as e:
            retry_count += 1
            logger.error(f"启动Celery Worker失败 (尝试 {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                logger.info(f"5秒后重试...")
                time.sleep(5)
            else:
                logger.error(f"启动Celery Worker失败，已达到最大重试次数")
        except KeyboardInterrupt:
            logger.info("Celery Worker已停止")
            break


def run_celery_beat(uid=None):
    """
    启动Celery Beat
    
    Args:
        uid: 运行Celery Beat的用户ID，如果为None则使用当前用户
    """
    logger.info("启动Celery Beat")
    
    # 设置NLTK数据目录环境变量
    nltk_data_dir = os.path.join(os.getcwd(), "data/nltk_data")
    os.environ["NLTK_DATA"] = nltk_data_dir
    logger.info(f"设置NLTK_DATA环境变量: {nltk_data_dir}")
    
    # 确保日志和调度文件目录存在
    data_dir = os.path.join(os.getcwd(), "data")
    ensure_dir_exists(data_dir)
    
    # 设置调度文件路径
    schedule_file = os.path.join(data_dir, "celerybeat-schedule")
    
    # 如果调度文件存在且可能损坏，尝试删除
    if os.path.exists(schedule_file):
        try:
            os.remove(schedule_file)
            logger.info(f"已删除可能损坏的调度文件: {schedule_file}")
        except Exception as e:
            logger.warning(f"无法删除调度文件: {e}")
    
    # 构建命令 - 移除不支持的-n选项
    cmd = [
        "celery", 
        "-A", 
        "app.workers.celery_app", 
        "beat", 
        "--loglevel=info",
        "--schedule", schedule_file
    ]
    
    # 如果指定了uid，添加--uid选项
    if uid is not None:
        cmd.extend(["--uid", str(uid)])
    
    # 最大重试次数
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            # 创建环境变量副本
            env = os.environ.copy()
            # 启动进程
            logger.info(f"执行命令: {' '.join(cmd)}")
            subprocess.run(cmd, check=True, env=env)
            break  # 如果成功，跳出循环
        except subprocess.CalledProcessError as e:
            retry_count += 1
            logger.error(f"启动Celery Beat失败 (尝试 {retry_count}/{max_retries}): {e}")
            if retry_count < max_retries:
                logger.info(f"5秒后重试...")
                time.sleep(5)
            else:
                logger.error(f"启动Celery Beat失败，已达到最大重试次数")
        except KeyboardInterrupt:
            logger.info("Celery Beat已停止")
            break


def main():
    """
    主函数，解析命令行参数并启动应用
    """
    parser = argparse.ArgumentParser(description="锦衣卫新闻监控分析系统")
    
    # API服务参数
    parser.add_argument("--host", type=str, default="0.0.0.0", help="主机地址")
    parser.add_argument("--port", type=int, default=8000, help="端口号")
    parser.add_argument("--reload", action="store_true", help="启用热重载")
    parser.add_argument("--workers", type=int, default=1, help="工作进程数")
    parser.add_argument("--auto-port", action="store_true", help="自动查找可用端口")
    
    # Celery参数
    parser.add_argument("--with-celery", action="store_true", help="同时启动Celery Worker")
    parser.add_argument("--with-beat", action="store_true", help="同时启动Celery Beat调度器")
    parser.add_argument("--celery-only", action="store_true", help="仅启动Celery服务（不启动API）")
    parser.add_argument("--celery-uid", type=str, help="指定运行Celery的用户ID或用户名")
    
    # 数据库参数
    parser.add_argument("--init-db", action="store_true", help="初始化数据库")
    
    args = parser.parse_args()
    
    # 初始化数据库
    if args.init_db:
        logger.info("正在初始化数据库...")
        try:
            import asyncio
            from app.db.init_db import init_db
            from app.db.session import get_db
            
            async def init() -> None:
                async for db in get_db():
                    await init_db(db)
                    break
            
            asyncio.run(init())
            logger.info("数据库初始化成功")
            return
        except Exception as e:
            logger.error(f"数据库初始化失败: {e}")
            return
    
    # 确保日志目录存在
    ensure_dir_exists("logs")
    
    # 确保数据目录存在
    data_dir = os.path.join(os.getcwd(), "data")
    ensure_dir_exists(data_dir)
    
    # 确保NLTK数据目录存在
    nltk_data_dir = os.path.join(data_dir, "nltk_data")
    ensure_dir_exists(nltk_data_dir)
    
    # 确定Celery用户ID
    celery_uid = None
    if args.celery_uid:
        # 尝试将输入解析为整数（用户ID）
        try:
            celery_uid = int(args.celery_uid)
            logger.info(f"使用用户ID {celery_uid} 运行Celery")
        except ValueError:
            # 如果不是整数，则假设是用户名
            celery_uid = get_uid_from_username(args.celery_uid)
            if celery_uid:
                logger.info(f"使用用户 {args.celery_uid} (uid={celery_uid}) 运行Celery")
            else:
                logger.error(f"无法找到用户 {args.celery_uid}，将使用当前用户运行Celery")
    # 如果是root用户且没有指定uid，尝试获取非root用户
    elif os.geteuid() == 0:
        celery_uid = get_non_root_user()
        if celery_uid:
            logger.info(f"使用非root用户(uid={celery_uid})运行Celery")
        else:
            logger.warning("当前用户为root，建议使用--celery-uid指定非root用户运行Celery")
    
    # 启动Celery Worker
    if args.with_celery or args.celery_only:
        celery_thread = threading.Thread(target=run_celery_worker, args=(celery_uid,))
        celery_thread.daemon = True
        celery_thread.start()
        logger.info("Celery Worker线程已启动")
        
        # 等待Celery Worker启动
        time.sleep(2)
    
    # 启动Celery Beat
    if args.with_beat or args.celery_only:
        beat_thread = threading.Thread(target=run_celery_beat, args=(celery_uid,))
        beat_thread.daemon = True
        beat_thread.start()
        logger.info("Celery Beat线程已启动")
        
        # 等待Celery Beat启动
        time.sleep(2)
    
    # 如果只启动Celery服务，则不启动API服务
    if args.celery_only:
        # 保持主线程运行
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("接收到中断信号，正在关闭服务...")
            return
    
    # 启动API服务
    if not args.celery_only:
        port = args.port
        
        # 检查端口是否被占用，如果被占用且设置了auto-port，则自动查找可用端口
        if is_port_in_use(port, args.host):
            if args.auto_port:
                new_port = find_available_port(port, args.host)
                logger.warning(f"端口 {port} 已被占用，使用新端口 {new_port}")
                port = new_port
            else:
                logger.error(f"端口 {port} 已被占用，请使用其他端口或添加 --auto-port 参数自动查找可用端口")
                return
        
        logger.info(f"启动API服务: host={args.host}, port={port}, reload={args.reload}, workers={args.workers}")
        uvicorn.run(
            "app.main:app",
            host=args.host,
            port=port,
            reload=args.reload,
            workers=args.workers,
        )


if __name__ == "__main__":
    main() 