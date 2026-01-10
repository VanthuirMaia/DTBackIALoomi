"""
Endpoints de autenticacao.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.auth import UserRegister, UserLogin, TokenResponse, UserResponse
from app.services.auth_service import auth_service
from app.models.user import UserRole

router = APIRouter(prefix="/auth", tags=["Autenticacao"])


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuario",
    description="Cria uma nova conta de usuario e retorna token JWT."
)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """Registra um novo usuario no sistema."""

    # Verifica se email ja existe
    existing_user = auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado"
        )

    # Cria usuario
    user = auth_service.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
        role=UserRole.USER
    )

    # Gera token
    token = auth_service.create_access_token(user)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login de usuario",
    description="Autentica usuario e retorna token JWT."
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Autentica usuario e retorna token JWT."""

    user = auth_service.authenticate_user(
        db=db,
        email=credentials.email,
        password=credentials.password
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"}
        )

    token = auth_service.create_access_token(user)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )


@router.post(
    "/register-admin",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar usuario admin",
    description="Cria uma conta de administrador. Apenas para setup inicial."
)
def register_admin(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Registra um usuario administrador.

    NOTA: Em producao, este endpoint deve ser protegido ou removido.
    Existe apenas para facilitar o setup inicial do sistema.
    """

    # Verifica se email ja existe
    existing_user = auth_service.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email ja cadastrado"
        )

    # Cria usuario admin
    user = auth_service.create_user(
        db=db,
        email=user_data.email,
        password=user_data.password,
        name=user_data.name,
        role=UserRole.ADMIN
    )

    # Gera token
    token = auth_service.create_access_token(user)

    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user)
    )
