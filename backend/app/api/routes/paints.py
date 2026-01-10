# Rotas CRUD para a entidade Tinta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import paint_repository
from app.models.user import User
from app.api.deps import get_admin_user

router = APIRouter(prefix="/paints", tags=["Paints"])


@router.get("/", summary="List all paints")
def list_paints(db: Session = Depends(get_db)):
    """Lista todas as tintas. Acesso publico."""
    return paint_repository.list_paints(db)


@router.get("/{paint_id}", summary="Get paint by ID")
def get_paint(paint_id: int, db: Session = Depends(get_db)):
    """Busca tinta por ID. Acesso publico."""
    paint = paint_repository.get_paint_by_id(db, paint_id)
    if not paint:
        raise HTTPException(status_code=404, detail="Paint not found")
    return paint


@router.post(
    "/",
    status_code=201,
    summary="Create a new paint",
    description="Cria uma nova tinta. Requer autenticacao de admin."
)
def create_paint(
    paint_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Cria nova tinta. Apenas admin."""
    paint = paint_repository.create_paint(db, paint_data)
    return paint


@router.put(
    "/{paint_id}",
    summary="Update paint by ID",
    description="Atualiza uma tinta existente. Requer autenticacao de admin."
)
def update_paint(
    paint_id: int,
    paint_data: dict,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Atualiza tinta. Apenas admin."""
    paint = paint_repository.update_paint(db, paint_id, paint_data)
    if not paint:
        raise HTTPException(status_code=404, detail="Paint not found")
    return paint


@router.delete(
    "/{paint_id}",
    status_code=204,
    summary="Delete paint by ID",
    description="Remove uma tinta. Requer autenticacao de admin."
)
def delete_paint(
    paint_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_admin_user)
):
    """Remove tinta. Apenas admin."""
    deleted = paint_repository.delete_paint(db, paint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Paint not found")
    return None
