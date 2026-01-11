"""
Servico de autenticacao com JWT e bcrypt.
"""

import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.schemas.auth import TokenPayload


# Configuracao de senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuracao JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "sua-chave-secreta-muito-segura-aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "1440"))  # 24 horas


class AuthService:
    """Servico de autenticacao."""

    @staticmethod
    def hash_password(password: str) -> str:
        """Gera hash bcrypt da senha."""
        return pwd_context.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifica se a senha corresponde ao hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(user: User) -> str:
        """Cria token JWT para o usuario."""
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        payload = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "exp": expire
        }

        return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def decode_token(token: str) -> Optional[TokenPayload]:
        """Decodifica e valida token JWT."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

            return TokenPayload(
                sub=int(payload["sub"]),
                email=payload["email"],
                role=UserRole(payload["role"]),
                exp=payload.get("exp")
            )
        except JWTError:
            return None

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Busca usuario por email."""
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
        """Busca usuario por ID."""
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        name: str,
        role: UserRole = UserRole.USER
    ) -> User:
        """Cria novo usuario."""
        user = User(
            email=email,
            password_hash=AuthService.hash_password(password),
            name=name,
            role=role
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """Autentica usuario por email e senha."""
        user = AuthService.get_user_by_email(db, email)

        if not user:
            return None

        if not AuthService.verify_password(password, user.password_hash):
            return None

        return user


# Instancia singleton
auth_service = AuthService()
