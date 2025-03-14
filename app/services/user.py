from typing import Any, Dict, Optional, Union, List
import uuid
from datetime import datetime, timedelta
import logging

from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate


async def get_user_by_email(db: AsyncSession, *, email: str) -> Optional[User]:
    """
    通过邮箱获取用户
    """
    result = await db.execute(select(User).where(User.email == email))
    return result.scalars().first()


async def get_user_by_username(db: AsyncSession, *, username: str) -> Optional[User]:
    """
    通过用户名获取用户
    """
    result = await db.execute(select(User).where(User.username == username))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, *, user_id: str) -> Optional[User]:
    """
    通过ID获取用户
    """
    try:
        # 尝试将字符串转换为UUID
        from uuid import UUID
        uuid_obj = UUID(user_id)
        result = await db.execute(select(User).where(User.id == uuid_obj))
        return result.scalars().first()
    except ValueError:
        # 如果无法转换为UUID，则返回None
        return None


async def get_user_by_reset_token(db: AsyncSession, *, token: str) -> Optional[User]:
    """
    通过重置令牌获取用户
    """
    result = await db.execute(select(User).where(User.reset_token == token))
    user = result.scalars().first()
    
    # 检查令牌是否过期
    if user and user.reset_token_expires_at and user.reset_token_expires_at > datetime.now():
        return user
    return None


async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    验证用户
    """
    from app.core.security import verify_password
    
    logger = logging.getLogger(__name__)
    logger.info(f"Authenticating user: {username}")
    logger.info(f"Password length: {len(password)}")
    
    # 尝试通过用户名查找用户
    user = await get_user_by_username(db, username=username)
    if user:
        logger.info(f"User found by username: {user.username}")
    else:
        logger.info(f"User not found by username, trying email: {username}")
        # 尝试通过邮箱查找用户
        user = await get_user_by_email(db, email=username)
        if user:
            logger.info(f"User found by email: {user.email}")
        else:
            logger.warning(f"User not found: {username}")
            return None
    
    logger.info(f"User found: {user.username}, checking password")
    logger.info(f"User hashed password: {user.hashed_password[:10]}...")
    
    # 检查登录尝试次数
    if user.login_attempts >= 5:  # 最多允许5次尝试
        logger.warning(f"Too many login attempts for user: {user.username}, attempts: {user.login_attempts}")
        # 更新登录尝试次数
        user.login_attempts += 1
        db.add(user)
        await db.commit()
        return None
    
    # 验证密码
    password_valid = verify_password(password, user.hashed_password)
    if not password_valid:
        logger.warning(f"Invalid password for user: {user.username}")
        # 更新登录尝试次数
        user.login_attempts += 1
        db.add(user)
        await db.commit()
        return None
    
    logger.info(f"Authentication successful for user: {user.username}")
    # 登录成功，重置登录尝试次数并更新最后登录时间
    user.login_attempts = 0
    user.last_login = datetime.now()
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


async def create_user(db: AsyncSession, *, user_in: UserCreate) -> User:
    """
    创建用户
    """
    from app.core.security import get_password_hash
    
    logger = logging.getLogger(__name__)
    logger.info(f"Creating user: {user_in.username}, {user_in.email}")
    
    try:
        hashed_password = get_password_hash(user_in.password)
        logger.info(f"Password hashed successfully for user: {user_in.username}")
        
        db_obj = User(
            email=user_in.email,
            username=user_in.username,
            hashed_password=hashed_password,
            full_name=user_in.full_name,
            is_active=user_in.is_active,
            is_superuser=user_in.is_superuser,
        )
        
        logger.info(f"User object created, adding to database: {db_obj.username}")
        db.add(db_obj)
        
        logger.info("Committing to database...")
        await db.commit()
        
        logger.info("Refreshing user object...")
        await db.refresh(db_obj)
        
        logger.info(f"User created successfully: {db_obj.username}, ID: {db_obj.id}")
        return db_obj
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        await db.rollback()
        raise


async def update_user(
    db: AsyncSession, *, db_obj: User, obj_in: Union[UserUpdate, Dict[str, Any]]
) -> User:
    """
    更新用户
    """
    from app.core.security import get_password_hash
    
    if isinstance(obj_in, dict):
        update_data = obj_in
    else:
        update_data = obj_in.dict(exclude_unset=True)
    
    if update_data.get("password"):
        hashed_password = get_password_hash(update_data["password"])
        del update_data["password"]
        update_data["hashed_password"] = hashed_password
    
    for field in update_data:
        if hasattr(db_obj, field):
            setattr(db_obj, field, update_data[field])
    
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj


async def create_reset_token(db: AsyncSession, *, email: str) -> Optional[str]:
    """
    创建密码重置令牌
    """
    user = await get_user_by_email(db, email=email)
    if not user:
        return None
    
    # 生成随机令牌
    reset_token = str(uuid.uuid4())
    
    # 设置令牌过期时间（24小时后）
    expires_at = datetime.now() + timedelta(hours=24)
    
    # 更新用户信息
    user.reset_token = reset_token
    user.reset_token_expires_at = expires_at
    db.add(user)
    await db.commit()
    
    return reset_token


async def reset_password(db: AsyncSession, *, token: str, new_password: str) -> bool:
    """
    重置密码
    """
    from app.core.security import get_password_hash
    
    user = await get_user_by_reset_token(db, token=token)
    if not user:
        return False
    
    # 更新密码
    user.hashed_password = get_password_hash(new_password)
    
    # 清除重置令牌
    user.reset_token = None
    user.reset_token_expires_at = None
    
    # 重置登录尝试次数
    user.login_attempts = 0
    
    db.add(user)
    await db.commit()
    
    return True


async def change_password(
    db: AsyncSession, *, user_id: str, current_password: str, new_password: str
) -> bool:
    """
    修改密码
    """
    from app.core.security import verify_password, get_password_hash
    
    user = await get_user_by_id(db, user_id=user_id)
    if not user:
        return False
    
    # 验证当前密码
    if not verify_password(current_password, user.hashed_password):
        return False
    
    # 更新密码
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    await db.commit()
    
    return True


async def reset_login_attempts(db: AsyncSession, *, user_id: str) -> bool:
    """
    重置登录尝试次数
    """
    user = await get_user_by_id(db, user_id=user_id)
    if not user:
        return False
    
    user.login_attempts = 0
    db.add(user)
    await db.commit()
    
    return True 