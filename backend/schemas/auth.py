from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    role: str = "user"
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    token: str
    user: UserResponse


class PlatformTokenExchangeRequest(BaseModel):
    platform_token: str


class TokenExchangeResponse(BaseModel):
    token: str
