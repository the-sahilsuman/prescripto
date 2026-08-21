"""Authentication controllers: refresh-token rotation, logout and password reset."""

from bson import ObjectId
from fastapi import HTTPException, status
from jose import JWTError, jwt as jose_jwt
from passlib.context import CryptContext

from config.mongodb import get_db
from middlewares.auth import (
    create_access_token,
    create_refresh_token,
    _secret,
    _ALGORITHM,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _credentials_error(message="Invalid or expired authentication credential. Please log in again."):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=message,
        headers={"WWW-Authenticate": "Bearer"},
    )


async def refresh_tokens(refresh_token: str):
    credentials_exc = _credentials_error()

    try:
        payload = jose_jwt.decode(refresh_token, _secret(), algorithms=[_ALGORITHM])
    except JWTError:
        raise credentials_exc

    sub = payload.get("sub")
    role = payload.get("role")
    tok_type = payload.get("type")

    if not sub or not role or tok_type != "refresh":
        raise credentials_exc

    db = get_db()
    stored = await db.refresh_tokens.find_one({"token": refresh_token})
    if not stored:
        raise credentials_exc

    # Rotate the refresh token so the old one cannot be reused.
    await db.refresh_tokens.delete_one({"token": refresh_token})

    new_access = create_access_token(sub=sub, role=role)
    new_refresh = create_refresh_token(sub=sub, role=role)

    await db.refresh_tokens.insert_one({
        "token": new_refresh,
        "role": role,
        "sub": sub,
    })

    return {
        "success": True,
        "token": new_access,
        "refreshToken": new_refresh,
    }


async def logout_user(refresh_token: str):
    """Revoke the current refresh token from MongoDB."""
    db = get_db()
    result = await db.refresh_tokens.delete_one({"token": refresh_token})

    return {
        "success": True,
        "message": "Logged out successfully",
        "revoked": result.deleted_count > 0,
    }


async def reset_password(account_type: str, account_id: str, email: str, new_password: str):
    """
    Reset a user's or doctor's password after verifying BOTH MongoDB ID and email.

    Password reset also revokes all existing refresh tokens for that account,
    forcing every old session to authenticate again.
    """
    if len(new_password) < 8:
        return {
            "success": False,
            "message": "Password must be at least 8 characters long",
        }

    if account_type not in {"user", "doctor"}:
        return {"success": False, "message": "Invalid account type"}

    try:
        object_id = ObjectId(account_id)
    except Exception:
        return {"success": False, "message": "Invalid ID"}

    collection_name = "users" if account_type == "user" else "doctors"
    db = get_db()
    collection = db[collection_name]

    account = await collection.find_one({
        "_id": object_id,
        "email": email,
    })

    if not account:
        return {
            "success": False,
            "message": "ID and email do not match",
        }

    hashed_password = pwd_context.hash(new_password)

    await collection.update_one(
        {"_id": object_id},
        {"$set": {"password": hashed_password}},
    )

    # A password change invalidates every previously issued refresh token
    # for this account, including tokens on other devices.
    await db.refresh_tokens.delete_many({
        "sub": account_id,
        "role": account_type,
    })

    return {
        "success": True,
        "message": "Password reset successfully. Please login with your new password.",
    }
