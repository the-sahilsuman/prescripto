"""
Token refresh controller.

Flow
────
1. Client sends the stored refreshToken to POST /api/auth/refresh.
2. We verify the JWT signature and expiry (python-jose does this automatically).
3. We look the token up in the `refresh_tokens` collection — if it isn't there
   the token has already been rotated or explicitly revoked, so we reject it.
4. We delete the old refresh token and issue a brand-new pair (rotate).
5. Client stores the new pair and continues seamlessly.
"""

from jose import JWTError, jwt as jose_jwt
from fastapi import HTTPException, status

from config.mongodb import get_db
from middlewares.auth import create_access_token, create_refresh_token, _secret, _ALGORITHM


async def refresh_tokens(refresh_token: str):
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token. Please log in again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # 1. Verify JWT signature + expiry
    try:
        payload = jose_jwt.decode(refresh_token, _secret(), algorithms=[_ALGORITHM])
    except JWTError:
        raise credentials_exc

    sub      = payload.get("sub")
    role     = payload.get("role")
    tok_type = payload.get("type")

    if not sub or not role or tok_type != "refresh":
        raise credentials_exc

    # 2. Check the token exists in DB (not yet rotated / revoked)
    db = get_db()
    stored = await db.refresh_tokens.find_one({"token": refresh_token})
    if not stored:
        raise credentials_exc

    # 3. Rotate — delete the old token, issue a fresh pair
    await db.refresh_tokens.delete_one({"token": refresh_token})

    new_access  = create_access_token(sub=sub,  role=role)
    new_refresh = create_refresh_token(sub=sub, role=role)

    await db.refresh_tokens.insert_one({"token": new_refresh, "role": role, "sub": sub})

    return {
        "success":      True,
        "token":        new_access,
        "refreshToken": new_refresh,
    }
