"""
Unified JWT authentication for Prescripto.

Two-token strategy
──────────────────
• Access token  — short-lived (ACCESS_TOKEN_EXPIRE_MINUTES, default 15 min).
                  Sent as  Authorization: Bearer <token>  on every API call.
• Refresh token — long-lived (REFRESH_TOKEN_EXPIRE_DAYS, default 7 days).
                  Stored in the `refresh_tokens` MongoDB collection and sent
                  only to POST /api/auth/refresh to obtain a new access token.
                  Rotated on every refresh (old one is deleted).

Token shape (both types share the same structure):
    {
        "sub":  "<user_id | doctor_id | admin_sentinel>",
        "role": "user" | "doctor" | "admin",
        "type": "access" | "refresh",
        "exp":  <unix timestamp>
    }

Usage in routes:
    from middlewares.auth import require_roles, CurrentUser

    @router.get("/dashboard")
    async def dashboard(current_user: CurrentUser = Depends(require_roles(["admin"]))):
        ...
"""

import os
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta
from typing import List

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

_ALGORITHM = "HS256"
_ACCESS_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "5"))   # default: 5 min
_REFRESH_EXPIRE_DAYS   = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS",   "7"))


def _secret() -> str:
    return os.getenv("JWT_SECRET", "")


# ── Token payload model ───────────────────────────────────────────────────────

@dataclass
class CurrentUser:
    sub:  str   # user_id / doctor_id / admin sentinel value
    role: str   # "user" | "doctor" | "admin"


# ── Token creation helpers ────────────────────────────────────────────────────

def create_access_token(sub: str, role: str) -> str:
    """Return a signed JWT access token that expires in ACCESS_TOKEN_EXPIRE_MINUTES."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=_ACCESS_EXPIRE_MINUTES)
    return jwt.encode(
        {"sub": sub, "role": role, "type": "access", "exp": expire},
        _secret(),
        algorithm=_ALGORITHM,
    )


def create_refresh_token(sub: str, role: str) -> str:
    """Return a signed JWT refresh token that expires in REFRESH_TOKEN_EXPIRE_DAYS."""
    expire = datetime.now(timezone.utc) + timedelta(days=_REFRESH_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": sub, "role": role, "type": "refresh", "exp": expire},
        _secret(),
        algorithm=_ALGORITHM,
    )


# ── Core dependency ───────────────────────────────────────────────────────────

async def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    """Decode Bearer access token → CurrentUser.  Raises 401 on any failure."""
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorised! Login Again",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, _secret(), algorithms=[_ALGORITHM])
    except JWTError:
        raise credentials_exc

    sub:       str | None = payload.get("sub")
    role:      str | None = payload.get("role")
    tok_type:  str | None = payload.get("type")

    # Reject refresh tokens used as access tokens (and vice-versa)
    if not sub or not role or tok_type != "access":
        raise credentials_exc

    return CurrentUser(sub=sub, role=role)


# ── Role-checker factory ──────────────────────────────────────────────────────

def require_roles(allowed: List[str]):
    """Return a FastAPI dependency that enforces role membership.

    Example
    -------
    @router.get("/dashboard")
    async def dashboard(current_user: CurrentUser = Depends(require_roles(["admin"]))):
        ...
    """
    async def _check(current_user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if current_user.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not Authorised! Login Again",
            )
        return current_user

    return _check
