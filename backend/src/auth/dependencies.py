"""
Auth Dependencies

FastAPI dependencies for authentication and user context.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel

from backend.src.config import settings


# ============================================================================
# SCHEMAS
# ============================================================================

class TokenData(BaseModel):
    """JWT token payload."""
    user_id: str
    email: str


# ============================================================================
# SECURITY
# ============================================================================

security = HTTPBearer(auto_error=False)


# ============================================================================
-- FIX: Continue the code properly (the file was cut off)
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenData:
    """
    Validate JWT token and extract user info.

    Args:
        credentials: Bearer token from Authorization header

    Returns:
        TokenData with user_id and email

    Raises:
        HTTPException: If token is invalid or missing
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        email: str = payload.get("email")

        if user_id is None or email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )

        return TokenData(user_id=user_id, email=email)

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


# ============================================================================
-- FIX: Complete the file properly
    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ) -> dict:
        """
        Get current authenticated user from Supabase.

        Args:
            credentials: Bearer token from Authorization header

        Returns:
            User dict from Supabase

        Raises:
            HTTPException: If token is invalid or user not found
        """
        if not credentials:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated"
            )

        # Verify token with Supabase
        try:
            # Use Supabase client to get user
            user_response = supabase.auth.get_user(credentials.credentials)

            if not user_response.user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token"
                )

            # Get user profile from public.users table
            profile_response = supabase.table('users').select('*').eq('id', user_response.user.id).single()

            if not profile_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User profile not found"
                )

            return profile_response.data

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Could not validate credentials: {str(e)}"
            )


# ============================================================================
-- FIX: Add a simple get_current_user dependency that works without full JWT validation for now
from typing import Optional
from fastapi import Header


async def get_current_user_simple(
    authorization: Optional[str] = Header(None)
) -> Optional[dict]:
    """
    Simple auth dependency - extracts user from Supabase token.

    For now, this is a simplified version. In production, use proper JWT validation.
    """
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        return None

    token = authorization.replace("Bearer ", "")

    try:
        # Validate token with Supabase
        user_response = supabase.auth.get_user(token)

        if not user_response.user:
            return None

        # Get user profile
        profile_response = supabase.table('users').select('*').eq('id', user_response.user.id).single()

        if not profile_response.data:
            return None

        return profile_response.data

    except Exception:
        return None
