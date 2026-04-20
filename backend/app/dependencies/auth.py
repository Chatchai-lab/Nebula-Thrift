"""FastAPI dependency for JWT-based authentication."""
from fastapi import Cookie, HTTPException
from jose import JWTError
from app.services.auth_service import decode_token


async def get_current_user(access_token: str | None = Cookie(default=None)) -> dict:
    """FastAPI dependency to get the current authenticated user from JWT cookie.

    Args:
        access_token: JWT token from HttpOnly cookie

    Returns:
        Decoded token payload with user_id and email

    Raises:
        HTTPException: 401 Unauthorized if token is missing or invalid
    """
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = decode_token(access_token)
        return payload  # {"user_id": str, "email": str, "exp": int}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
