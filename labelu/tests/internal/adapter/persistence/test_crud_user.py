from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.common.security import verify_password
from labelu.internal.common.security import get_password_hash

from labelu.tests.utils.utils import random_username
from labelu.tests.utils.utils import random_lower_string


def test_create_user(db: Session) -> None:
    username = random_username()
    password = random_lower_string()
    user_in = User(username=username, hashed_password=get_password_hash(password))
    with db.begin():
        user = crud_user.create(db, user=user_in)
    assert user.username == username
    assert hasattr(user, "hashed_password")


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_username()
    user_in = User(username=username, hashed_password=get_password_hash(password))
    with db.begin():
        user = crud_user.create(db, user=user_in)
    user_2 = crud_user.get(db, id=user.id)
    assert user_2
    assert user.username == user_2.username
    assert jsonable_encoder(user) == jsonable_encoder(user_2)


def test_get_user_by_username(db: Session) -> None:
    password = random_lower_string()
    username = random_username()
    user_in = User(username=username, hashed_password=get_password_hash(password))
    with db.begin():
        user = crud_user.create(db, user=user_in)
    user_2 = crud_user.get_user_by_username(db, username=user_in.username)
    assert user_2
    assert user.username == user_2.username
    assert jsonable_encoder(user) == jsonable_encoder(user_2)
