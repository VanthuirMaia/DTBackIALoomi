# Rotas CRUD para a entidade Tinta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories import paint_repository

router = APIRouter(prefix="/paints", tags=["Paints"])


@router.post("/", status_code=201, summary="Create a new paint")
def create_paint(paint_data: dict, db: Session = Depends(get_db)):
    paint = paint_repository.create_paint(db, paint_data)
    return paint


@router.get("/", summary="List all paints")
def list_paints(db: Session = Depends(get_db)):
    return paint_repository.list_paints(db)


@router.get("/{paint_id}", summary="Get paint by ID")
def get_paint(paint_id: int, db: Session = Depends(get_db)):
    paint = paint_repository.get_paint_by_id(db, paint_id)
    if not paint:
        raise HTTPException(status_code=404, detail="Paint not found")
    return paint


@router.put("/{paint_id}", summary="Update paint by ID")
def update_paint(paint_id: int, paint_data: dict, db: Session = Depends(get_db)):
    paint = paint_repository.update_paint(db, paint_id, paint_data)
    if not paint:
        raise HTTPException(status_code=404, detail="Paint not found")
    return paint


@router.delete("/{paint_id}", status_code=204, summary="Delete paint by ID")
def delete_paint(paint_id: int, db: Session = Depends(get_db)):
    deleted = paint_repository.delete_paint(db, paint_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Paint not found")
    return None
