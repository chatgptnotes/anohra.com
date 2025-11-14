from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import timedelta

from auth.jwt_handler import (
    verify_password,
    create_access_token,
    decode_access_token,
    Token,
    User,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from database.user_db import create_user, get_user_by_email

router = APIRouter(prefix="/api/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class UserRegister(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


class UserResponse(BaseModel):
    email: str
    full_name: Optional[str] = None
    message: str


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user from token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = decode_access_token(token)
    if token_data is None or token_data.email is None:
        raise credentials_exception

    user = await get_user_by_email(token_data.email)
    if user is None:
        raise credentials_exception

    return User(email=user.email, full_name=user.full_name, disabled=user.disabled)


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user (not disabled)"""
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@router.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """
    Register a new user
    """
    try:
        # Check if user already exists
        existing_user = await get_user_by_email(user_data.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        new_user = await create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )

        return UserResponse(
            email=new_user["email"],
            full_name=new_user["full_name"],
            message="User registered successfully"
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Login with email and password to get access token
    """
    # Get user from database
    user = await get_user_by_email(form_data.username)  # username field contains email

    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User account is disabled"
        )

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )

    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information
    """
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_active_user)):
    """
    Logout (client should delete the token)
    """
    return {"message": "Successfully logged out"}
