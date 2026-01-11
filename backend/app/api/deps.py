"""
Dependencias de autenticacao e autorizacao para FastAPI.
"""

from typing import List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User, UserRole
from app.services.auth_service import auth_service

# Esquema de seguranca Bearer
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependencia que extrai e valida o usuario do token JWT.

    Uso:
        @router.get("/protected")
        def protected_route(user: User = Depends(get_current_user)):
            ...
    """
    token = credentials.credentials

    # Decodifica token
    payload = auth_service.decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalido ou expirado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    # Busca usuario
    user = auth_service.get_user_by_id(db, payload.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario nao encontrado",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user


def require_roles(allowed_roles: List[UserRole]):
    """
    Factory de dependencia para verificar roles.

    Uso:
        @router.get("/admin-only")
        def admin_route(user: User = Depends(require_roles([UserRole.ADMIN]))):
            ...
    """
    def role_checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Acesso negado. Roles permitidos: {[r.value for r in allowed_roles]}"
            )
        return user

    return role_checker


# Dependencias pre-configuradas para uso comum
def get_admin_user(user: User = Depends(require_roles([UserRole.ADMIN]))) -> User:
    """Dependencia que exige usuario admin."""
    return user


def get_authenticated_user(user: User = Depends(get_current_user)) -> User:
    """Dependencia que exige usuario autenticado (qualquer role)."""
    return user
