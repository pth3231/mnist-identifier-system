from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta

from models.user import User
from models.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from utils.jwt_helper import create_access_token
from utils.models_converter import convert_user_to_response

from utils.auth_helper import (
    hash_password,
    verify_password
)

from utils.database import (
    find_user_by_id,
    get_db,
    find_user_by_username,
    find_user_by_email
)

router = APIRouter()

@router.post("/sign-up", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    credentials: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Sign up a new user"""
    
    # Check if username already exists
    existed_user = await find_user_by_username(credentials.username, db)
    
    if existed_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existed_email = await find_user_by_email(credentials.email, db)
    if existed_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = hash_password(credentials.password)
    new_user = User(
        username=credentials.username,
        email=credentials.email,
        password_hash=hashed_password
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/sign-in", response_model=TokenResponse)
async def sign_in(
    credentials: UserLogin,
    db: AsyncSession = Depends(get_db)
) -> TokenResponse:
    """Sign in a user and return access token"""
    
    # Find user by username
    user = await find_user_by_username(credentials.username, db)
    
    if not user or not verify_password(credentials.password, user.password_hash):
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
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=convert_user_to_response(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get current authenticated user information"""
    user = await find_user_by_id(user_id, db)

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found or inactive"
        )
    
    return convert_user_to_response(user)
