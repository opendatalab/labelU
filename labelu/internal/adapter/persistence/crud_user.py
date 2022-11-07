from sqlalchemy.orm import Session
from labelu.internal.domain.models.user import User


def get_user(db: Session, id: str) -> User:
    return db.query(User).filter(User.id == id).first()


def get_user_by_username(db: Session, username: str) -> User:
    return db.query(User).filter(User.username == username).first()


def create_user(db: Session, user: User) -> User:
    db_user = User(username=user.username, hashed_password=user.hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
