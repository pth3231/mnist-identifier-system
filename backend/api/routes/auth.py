from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta
import logging

from models.user import User
from models.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from utils.jwt_helper import create_access_token
from utils.redis_utils import set_user_cache

from utils.auth_helper import (
    hash_password,
    verify_password
)

from utils.database import (
    get_db,
    find_user_by_username,
    find_user_by_email,
    get_current_user
)


logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sign-up", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Sign up a new user"""
    
    # Check if username already exists
    existed_user = await find_user_by_username(user_data.username, db)
    
    if existed_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existed_email = await find_user_by_email(user_data.email, db)
    if existed_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    logger.info(f"New user created: {new_user.username} ({new_user.email})")
    
    return new_user


@router.post("/sign-in", response_model=TokenResponse)
async def sign_in(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """Sign in a user and return access token"""
    
    # Find user by username
    user = await find_user_by_username(credentials.username, db)
    
    if not user or not verify_password(credentials.password, user.password_hash):
        logger.warning(f"Failed sign-in attempt for username: {credentials.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    # Generate access token
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username},
        expires_delta=timedelta(minutes=30)
    )
    
    # Cache user data for faster lookups
    user_data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "is_active": user.is_active
    }
    await set_user_cache(user.id, user_data, ttl=1800)  # 30 minutes
    logger.info(f"User signed in: {user.username}")
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user information"""
    return current_user
