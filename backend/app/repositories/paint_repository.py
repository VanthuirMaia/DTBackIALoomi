# Repositório de acesso a dados para a entidade Tinta

from sqlalchemy.orm import Session

from app.models.paint import Paint


def create_paint(db: Session, paint_data: dict) -> Paint:
    paint = Paint(**paint_data)
    db.add(paint)
    db.commit()
    db.refresh(paint)
    return paint


def get_paint_by_id(db: Session, paint_id: int) -> Paint | None:
    return db.query(Paint).filter(Paint.id == paint_id).first()


def list_paints(db: Session) -> list[Paint]:
    return db.query(Paint).all()


def update_paint(db: Session, paint_id: int, paint_data: dict) -> Paint | None:
    paint = get_paint_by_id(db, paint_id)
    if not paint:
        return None
    allowed_fields = {
        "nome",
        "cor",
        "tipo_superficie",
        "ambiente",
        "acabamento",
        "features",
        "linha",
    }
    for key, value in paint_data.items():
        if key in allowed_fields:
            setattr(paint, key, value)
    db.commit()
    db.refresh(paint)
    return paint


def delete_paint(db: Session, paint_id: int) -> bool:
    paint = get_paint_by_id(db, paint_id)
    if not paint:
        return False
    db.delete(paint)
    db.commit()
    return True
