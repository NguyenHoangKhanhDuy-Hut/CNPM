import logging

from core.auth import AccessTokenError, decode_access_token
from core.database import get_db
from dependencies.auth import get_current_user, get_bearer_token
from fastapi import APIRouter, Depends, HTTPException, status
from schemas.auth import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    UserResponse,
)
from services.auth import AuthService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])
logger = logging.getLogger(__name__)


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    try:
        user = auth_service.register_user(
            email=payload.email.strip().lower(),
            password=payload.password,
            name=payload.name.strip() if payload.name else None,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))

    token, _, _ = auth_service.issue_app_token(user)
    return LoginResponse(token=token, user=UserResponse.model_validate(user))


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    auth_service = AuthService(db)
    user = auth_service.authenticate_user(email=payload.email.strip().lower(), password=payload.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    token, _, _ = auth_service.issue_app_token(user)
    return LoginResponse(token=token, user=UserResponse.model_validate(user))


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    return current_user


@router.post("/logout")
def logout(token: str = Depends(get_bearer_token)):
    try:
        decode_access_token(token)
    except AccessTokenError:
        pass
    return {"message": "Logged out successfully"}