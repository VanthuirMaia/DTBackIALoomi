"""
Schemas Pydantic para autenticacao.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserRegister(BaseModel):
    """Schema para registro de usuario."""
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimo 6 caracteres")
    name: str = Field(..., min_length=2, max_length=255)


class UserLogin(BaseModel):
    """Schema para login de usuario."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema de resposta com dados do usuario."""
    id: int
    email: str
    name: str
    role: UserRole

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema de resposta com token JWT."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenPayload(BaseModel):
    """Schema do payload do token JWT."""
    sub: int  # user_id
    email: str
    role: UserRole
    exp: Optional[int] = None
