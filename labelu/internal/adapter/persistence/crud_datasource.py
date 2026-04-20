from typing import Optional, List, Tuple
from datetime import datetime

from sqlalchemy.orm import Session

from labelu.internal.domain.models.data_source import DataSource


def create(db: Session, data_source: DataSource) -> DataSource:
    db.add(data_source)
    db.flush()
    db.refresh(data_source)
    return data_source


def get(db: Session, ds_id: int) -> Optional[DataSource]:
    return (
        db.query(DataSource)
        .filter(DataSource.id == ds_id, DataSource.deleted_at.is_(None))
        .first()
    )


def list_by_user(
    db: Session, user_id: int, page: int = 0, size: int = 100
) -> Tuple[List[DataSource], int]:
    query = db.query(DataSource).filter(
        DataSource.created_by == user_id, DataSource.deleted_at.is_(None)
    )
    total = query.count()
    items = query.order_by(DataSource.id.desc()).offset(page * size).limit(size).all()
    return items, total


def update(db: Session, db_obj: DataSource, obj_in: dict) -> DataSource:
    for k, v in obj_in.items():
        setattr(db_obj, k, v)
    db.flush()
    db.refresh(db_obj)
    return db_obj


def soft_delete(db: Session, db_obj: DataSource) -> None:
    db_obj.deleted_at = datetime.now()
    db.flush()
