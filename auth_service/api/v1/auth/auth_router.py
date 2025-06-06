from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.api.v1.auth.auth_schemas import (
    LoginRequest,
    NewPassword,
    PasswordReset,
    RefreshToken,
    UserCreate,
)
from auth_service.core.services.service import AuthService
from libs.db import get_async_db
from fastapi_limiter.depends import RateLimiter

# Create router with auth tag
auth_router = APIRouter(tags=["Auth"], prefix="/auth")

# Set up OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Common dependency for auth service
async def get_auth_service(db: AsyncSession = Depends(get_async_db)) -> AuthService:
    return AuthService(db)


# User registration endpoint - Limit to 5 registrations per IP address in 5 minutes
@auth_router.post("/register", status_code=204, dependencies=[Depends(RateLimiter(times=5, seconds=300))])
async def register_user(user_data: UserCreate, auth_service: AuthService = Depends(get_auth_service)):
    await auth_service.create_user(user_data)


# Login endpoint - Limit to 10 login attempts per IP address in 1 minute
@auth_router.post("/login", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
async def login(login_data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.authenticate_user_by_email(login_data)


# Token refresh endpoint
@auth_router.post("/refresh-token")
async def refresh_access_token(refresh_token: RefreshToken, auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.refresh_token(refresh_token)


# Current user profile endpoint
@auth_router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme), auth_service: AuthService = Depends(get_auth_service)):
    return await auth_service.get_current_user(token)


# Password reset request endpoint
@auth_router.post("/password-reset/request", status_code=204)
async def request_password_reset(email_data: PasswordReset, auth_service: AuthService = Depends(get_auth_service)):
    await auth_service.request_password_reset(email_data)


# Password reset completion endpoint
@auth_router.post("/password-reset/{reset_token}", status_code=204)
async def reset_password(
    reset_token: str, password_data: NewPassword, auth_service: AuthService = Depends(get_auth_service)
):
    await auth_service.reset_password(reset_token, password_data.password)
