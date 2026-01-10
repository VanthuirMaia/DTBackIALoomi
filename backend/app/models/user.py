"""
Modelo de Usuario para autenticacao.
"""

from enum import Enum as PyEnum
from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.sql import func

from app.db.base import Base


class UserRole(str, PyEnum):
    """Roles disponiveis no sistema."""
    ADMIN = "admin"
    USER = "user"


class User(Base):
    """Modelo ORM de Usuario."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
