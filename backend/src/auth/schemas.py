"""
Auth Schemas

Pydantic models for authentication requests and responses.
"""

from pydantic import BaseModel, EmailStr
from typing import Optional


class SignupRequest(BaseModel):
    """Signup request schema."""
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Auth response schema."""
    access_token: str
    user: dict
    message: str


class UserResponse(BaseModel):
    """User profile response."""
    id: str
    email: str
    name: Optional[str] = None
    avatar_url: Optional[str] = None
    created_at: str
