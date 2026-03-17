"""
Auth Router

Authentication endpoints - signup, login, get current user.
"""

from fastapi import APIRouter, HTTPException, status
from supabase import AuthApiError

from src.auth.schemas import SignupRequest, LoginRequest, AuthResponse, UserResponse
from src.database import supabase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def signup(request: SignupRequest) -> AuthResponse:
    """
    Register a new user.

    Args:
        request: Signup request with email, password, name

    Returns:
        AuthResponse with access token and user info

    Raises:
        HTTPException: If signup fails
    """
    try:
        # Sign up with Supabase Auth
        auth_response = supabase.auth.sign_up({
            "email": request.email,
            "password": request.password,
            "options": {
                "data": {
                    "name": request.name
                }
            }
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to create user"
            )

        # Get session token
        session = supabase.auth.get_session()
        access_token = session.access_token if session else ""

        # Get user profile from public.users (created by trigger)
        profile_response = supabase.table('users').select('*').eq('id', auth_response.user.id).single()

        return AuthResponse(
            access_token=access_token,
            user=profile_response.data if profile_response.data else {
                "id": auth_response.user.id,
                "email": auth_response.user.email,
                "name": request.name
            },
            message="User created successfully"
        )

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(e)}"
        )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest) -> AuthResponse:
    """
    Login existing user.

    Args:
        request: Login request with email, password

    Returns:
        AuthResponse with access token and user info

    Raises:
        HTTPException: If login fails
    """
    try:
        # Sign in with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            "email": request.email,
            "password": request.password
        })

        if not auth_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Get session token
        session = supabase.auth.get_session()
        access_token = session.access_token if session else ""

        # Get user profile
        profile_response = supabase.table('users').select('*').eq('id', auth_response.user.id).single()

        return AuthResponse(
            access_token=access_token,
            user=profile_response.data if profile_response.data else {
                "id": auth_response.user.id,
                "email": auth_response.user.email
            },
            message="Login successful"
        )

    except AuthApiError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user(authorization: str) -> UserResponse:
    """
    Get current authenticated user profile.

    Args:
        authorization: Bearer token from Authorization header

    Returns:
        UserResponse with user profile

    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token = authorization.replace("Bearer ", "")

    try:
        # Verify token with Supabase
        user_response = supabase.auth.get_user(token)

        if not user_response.user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        # Get user profile
        profile_response = supabase.table('users').select('*').eq('id', user_response.user.id).single()

        if not profile_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User profile not found"
            )

        return UserResponse(**profile_response.data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}"
        )
