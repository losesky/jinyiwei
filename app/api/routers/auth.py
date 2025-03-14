from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, get_current_active_user
from app.db.session import get_db
from app.schemas.token import Token
from app.schemas.user import User, UserCreate, PasswordResetRequest, PasswordResetConfirm, PasswordChange
from app.services.user import (
    authenticate_user, create_user, get_user_by_email, get_user_by_username, 
    create_reset_token, reset_password, change_password
)
from app.services.email import send_reset_password_email

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(
    db: AsyncSession = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 兼容的令牌登录，获取访问令牌
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Login attempt for username: {form_data.username}")
    logger.info(f"Form data: {form_data}")
    logger.info(f"Password length: {len(form_data.password)}")
    
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.warning(f"Authentication failed for username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码不正确",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        logger.warning(f"Inactive user attempted to login: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="用户未激活",
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = create_access_token(user.id, expires_delta=access_token_expires)
    logger.info(f"Login successful for user: {user.username}, token generated")
    
    return {
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/register", response_model=User)
async def register_user(
    *,
    db: AsyncSession = Depends(get_db),
    user_in: UserCreate,
) -> Any:
    """
    注册新用户
    """
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"Registering new user: {user_in.username}, {user_in.email}")
    logger.info(f"Registration data: {user_in.dict(exclude={'password'})}")
    logger.info(f"Password length: {len(user_in.password)}")
    
    # 检查用户名是否已存在
    existing_user = await get_user_by_username(db, username=user_in.username)
    if existing_user:
        logger.warning(f"Username already exists: {user_in.username}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该用户名已被注册",
        )
    
    # 检查邮箱是否已存在
    existing_email = await get_user_by_email(db, email=user_in.email)
    if existing_email:
        logger.warning(f"Email already exists: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该邮箱已被注册",
        )
    
    try:
        # 确保full_name不是空字符串
        if user_in.full_name == "":
            user_in.full_name = None
            
        logger.info(f"Processed registration data: {user_in.dict(exclude={'password'})}")
        user = await create_user(db, user_in=user_in)
        logger.info(f"User registered successfully: {user.username}")
        return user
    except Exception as e:
        logger.error(f"Error registering user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"注册失败: {str(e)}",
        )


@router.post("/password-reset/request", response_model=dict)
async def request_password_reset(
    *,
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks,
    reset_request: PasswordResetRequest,
) -> Any:
    """
    请求密码重置
    """
    user = await get_user_by_email(db, email=reset_request.email)
    if not user:
        # 即使用户不存在，也返回成功，以防止用户枚举
        return {"message": "如果该邮箱已注册，您将收到一封密码重置邮件"}
    
    # 创建重置令牌
    token = await create_reset_token(db, email=reset_request.email)
    
    # 发送重置邮件
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    background_tasks.add_task(
        send_reset_password_email,
        email_to=user.email,
        username=user.username,
        reset_url=reset_url
    )
    
    return {"message": "如果该邮箱已注册，您将收到一封密码重置邮件"}


@router.post("/password-reset/confirm", response_model=dict)
async def confirm_password_reset(
    *,
    db: AsyncSession = Depends(get_db),
    reset_confirm: PasswordResetConfirm,
) -> Any:
    """
    确认密码重置
    """
    result = await reset_password(db, token=reset_confirm.token, new_password=reset_confirm.new_password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效或已过期的重置令牌",
        )
    
    return {"message": "密码已成功重置"}


@router.post("/password-change", response_model=dict)
async def change_user_password(
    *,
    db: AsyncSession = Depends(get_db),
    password_change: PasswordChange,
    current_user: User = Depends(get_current_active_user),
) -> Any:
    """
    修改密码
    """
    result = await change_password(
        db, 
        user_id=str(current_user.id), 
        current_password=password_change.current_password, 
        new_password=password_change.new_password
    )
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="当前密码不正确",
        )
    
    return {"message": "密码已成功修改"} 