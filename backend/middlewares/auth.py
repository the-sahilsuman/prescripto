import os
from fastapi import Header, HTTPException
from jose import jwt, JWTError


def _secret() -> str:
    return os.getenv("JWT_SECRET", "")


# ── Admin auth ────────────────────────────────────────────────────────────────
# The original JS did:  jwt.sign(email+password, secret)   (raw string payload)
# python-jose always works with dicts, so we store the value in {"sub": ...}
# and verify it here.

async def auth_admin(atoken: str = Header(default=None)):
    if not atoken:
        raise HTTPException(status_code=401, detail="Not Authorised! Login Again")
    try:
        payload = jwt.decode(atoken, _secret(), algorithms=["HS256"])
        expected = os.getenv("ADMIN_EMAIL", "") + os.getenv("ADMIN_PASSWORD", "")
        if payload.get("sub") != expected:
            raise HTTPException(status_code=401, detail="Not Authorised! Login Again")
    except JWTError:
        raise HTTPException(status_code=401, detail="Not Authorised! Login Again")


# ── Doctor auth ───────────────────────────────────────────────────────────────

async def auth_doctor(dtoken: str = Header(default=None)) -> str:
    if not dtoken:
        raise HTTPException(status_code=401, detail="Not Authorised! Login Again")
    try:
        payload = jwt.decode(dtoken, _secret(), algorithms=["HS256"])
        doc_id = payload.get("id")
        if not doc_id:
            raise HTTPException(status_code=401, detail="Not Authorised! Login Again")
        return doc_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Not Authorised! Login Again")


# ── User auth ─────────────────────────────────────────────────────────────────

async def auth_user(token: str = Header(default=None)) -> str:
    if not token:
        raise HTTPException(status_code=401, detail="Not Authorised! Login Again")
    try:
        payload = jwt.decode(token, _secret(), algorithms=["HS256"])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Not Authorised! Login Again")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="Not Authorised! Login Again")
