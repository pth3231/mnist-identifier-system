from fastapi import APIRouter, HTTPException, status, Depends, Request

from utils.jwt_helper import get_token_from_header, verify_token
from models.schemas import UserCreate, UserLogin, UserResponse, TokenResponse
from config import settings
from utils.httpx_helper import get, post

router = APIRouter()


@router.post("/sign-up", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def sign_up(
    credentials: UserCreate,
    request: Request
) -> UserResponse:
    """Sign up a new user"""
    return await post(
        url=f"{settings.AUTH_URL}/auth/sign-up",
        request=request,
        json_data=credentials.model_dump()
    )

@router.post("/sign-in", response_model=TokenResponse)
async def sign_in(
    credentials: UserLogin,
    request: Request
):
    """Sign in a user and return access token"""
    return await post(
        url=f"{settings.AUTH_URL}/auth/sign-in",
        request=request,
        json_data=credentials.model_dump()
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    request: Request,
    payload: dict = Depends(verify_token),
    token: str = Depends(get_token_from_header)
):
    """Get current authenticated user information"""
    user_id: str = payload.get("sub")

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user_id: int
    try:
        user_id: int = int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format"
        )

    return await get(
        url=f"{settings.AUTH_URL}/auth/me",
        request=request,
        headers={
            "Authorization": f"Bearer {token}"
        },
        params={"user_id": user_id}
    )
