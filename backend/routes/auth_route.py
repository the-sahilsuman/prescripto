from fastapi import APIRouter
from pydantic import BaseModel, EmailStr

from controllers.auth_controller import refresh_tokens, logout_user, reset_password

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class RefreshBody(BaseModel):
    refreshToken: str


class ForgotPasswordBody(BaseModel):
    accountType: str
    accountId: str
    email: EmailStr
    newPassword: str


@router.post("/refresh")
async def route_refresh(body: RefreshBody):
    return await refresh_tokens(body.refreshToken)


@router.post("/logout")
async def route_logout(body: RefreshBody):
    return await logout_user(body.refreshToken)


@router.post("/forgot-password")
async def route_forgot_password(body: ForgotPasswordBody):
    return await reset_password(
        account_type=body.accountType,
        account_id=body.accountId,
        email=body.email,
        new_password=body.newPassword,
    )
