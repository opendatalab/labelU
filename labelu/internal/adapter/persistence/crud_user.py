from typing import List, Tuple

from sqlalchemy.orm import Session
from labelu.internal.domain.models.user import User


def create(db: Session, user: User) -> User:
    db_user = User(username=user.username, hashed_password=user.hashed_password)
    db.add(db_user)
    db.flush()
    db.refresh(db_user)
    return db_user


def get(db: Session, id: int) -> User:
    return db.query(User).filter(User.id == id).first()


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()

def list_by(db: Session, page: int, size: int, username: str = None) -> Tuple[List[User], int]:
    query_filter = []
    
    if username:
        query_filter.append(User.username == username)
    
    query = db.query(User).filter(*query_filter)
    result = (
        query
        .order_by(User.id.desc())
        .offset(offset=page * size)
        .limit(limit=size)
        .all()
    )
    total = query.count()
    return result, total

def list_by_ids(db: Session, ids: List[int]) -> List[User]:
    return db.query(User).filter(User.id.in_(ids)).all()