from fastapi import APIRouter
from pydantic import BaseModel

from controllers.auth_controller import refresh_tokens

router = APIRouter(prefix="/api/auth", tags=["Auth"])


class RefreshBody(BaseModel):
    refreshToken: str


@router.post("/refresh")
async def route_refresh(body: RefreshBody):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    return await refresh_tokens(body.refreshToken)
