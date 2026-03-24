from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.security import APIKeyHeader
from pydantic import BaseModel, EmailStr
from typing import Optional
from src.services.auth import get_auth, AuthService, User

router = APIRouter(prefix="/auth", tags=["Authentication"])

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    user_id: str
    username: str
    email: str
    api_key: str
    message: str


class LoginResponse(BaseModel):
    user_id: str
    username: str
    api_key: str
    message: str


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, auth: AuthService = Depends(get_auth)):
    for user in auth.get_all_users():
        if user.username == request.username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if user.email == request.email:
            raise HTTPException(status_code=400, detail="Email already exists")

    user = auth.create_user(
        username=request.username, email=request.email, password=request.password
    )

    return AuthResponse(
        user_id=user.id,
        username=user.username,
        email=user.email,
        api_key=user.api_key,
        message="Registration successful",
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, auth: AuthService = Depends(get_auth)):
    user = auth.authenticate(request.username, request.password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")

    return LoginResponse(
        user_id=user.id,
        username=user.username,
        api_key=user.api_key,
        message="Login successful",
    )


@router.get("/me")
async def get_me(
    api_key: str = Depends(api_key_header), auth: AuthService = Depends(get_auth)
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    user = auth.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "created_at": user.created_at.isoformat(),
        "is_active": user.is_active,
    }


@router.post("/refresh")
async def refresh_api_key(
    api_key: str = Depends(api_key_header), auth: AuthService = Depends(get_auth)
):
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")

    user = auth.get_user_by_api_key(api_key)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid API key")

    new_api_key = auth.generate_api_key()
    user.api_key = new_api_key

    return {
        "user_id": user.id,
        "username": user.username,
        "api_key": new_api_key,
        "message": "API key refreshed",
    }
