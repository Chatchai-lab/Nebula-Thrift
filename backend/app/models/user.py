"""User account models."""
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Request model for user registration."""
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class UserOut(BaseModel):
    """Response model for user information (no password)."""
    user_id: str
    name: str
    email: str
    created_at: str
