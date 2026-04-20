"""Authentication routes: register, login, logout, me."""
import os
from fastapi import APIRouter, HTTPException, Response, Depends
from app.models.user import UserCreate, UserLogin, UserOut
from app.services.user_service import UserService
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["auth"])

IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"


@router.post("/register", response_model=UserOut)
async def register(user_create: UserCreate, response: Response) -> UserOut:
    """Register a new user account.

    Args:
        user_create: Email, password, and name
        response: FastAPI Response to set cookie

    Returns:
        UserOut with user_id, name, email, created_at

    Raises:
        HTTPException: 400 if email already in use, 500 on server error
    """
    try:
        user_service = UserService()

        # Hash password
        hashed_pw = hash_password(user_create.password)

        # Create user in Cosmos DB
        user = user_service.create(user_create.name, user_create.email, hashed_pw)

        # Create JWT token
        token = create_access_token(user["user_id"], user["email"])

        # Set HttpOnly cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=1800,  # 30 minutes
            samesite="lax",
            secure=IS_PRODUCTION,  # HTTPS only in production
        )

        return UserOut(**user)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@router.post("/login", response_model=UserOut)
async def login(user_login: UserLogin, response: Response) -> UserOut:
    """Log in with email and password.

    Args:
        user_login: Email and password
        response: FastAPI Response to set cookie

    Returns:
        UserOut with user_id, name, email, created_at

    Raises:
        HTTPException: 401 if credentials invalid, 500 on server error
    """
    try:
        user_service = UserService()

        # Load user by email
        user_doc = user_service.get_by_email(user_login.email)
        if not user_doc:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Verify password
        if not verify_password(user_login.password, user_doc.get("hashed_password", "")):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        # Create JWT token
        token = create_access_token(user_doc["user_id"], user_doc["email"])

        # Set HttpOnly cookie
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=1800,
            samesite="lax",
            secure=IS_PRODUCTION,
        )

        return UserOut(
            user_id=user_doc["user_id"],
            name=user_doc["name"],
            email=user_doc["email"],
            created_at=user_doc["created_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {str(e)}")


@router.post("/logout")
async def logout(response: Response) -> dict:
    """Log out by clearing the JWT cookie.

    Args:
        response: FastAPI Response to clear cookie

    Returns:
        Success message
    """
    response.delete_cookie(key="access_token", samesite="lax")
    return {"status": "success", "message": "Logged out"}


@router.get("/me", response_model=UserOut)
async def get_current_user_info(current_user: dict = Depends(get_current_user)) -> UserOut:
    """Get the current authenticated user's information.

    Args:
        current_user: Injected by get_current_user dependency

    Returns:
        UserOut with current user info
    """
    try:
        user_service = UserService()

        # Fetch full user doc from DB (current_user only has user_id and email from JWT)
        user_doc = user_service.get_by_id(current_user["user_id"])
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        return UserOut(**user_doc)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user: {str(e)}")


# Dependency to protect routes
__all__ = ["router"]
