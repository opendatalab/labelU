from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.common.security import verify_password
from labelu.internal.common.security import get_password_hash

from labelu.tests.utils.utils import random_email
from labelu.tests.utils.utils import random_lower_string


def test_create_user(db: Session) -> None:
    email = random_email()
    password = random_lower_string()
    user_in = User(email=email, hashed_password=get_password_hash(password))
    user = crud_user.create_user(db, user=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


def test_get_user(db: Session) -> None:
    password = random_lower_string()
    username = random_email()
    user_in = User(email=username, hashed_password=get_password_hash(password))
    user = crud_user.create_user(db, user=user_in)
    user_2 = crud_user.get_user_by_email(db, email=user_in.email)
    assert user_2
    assert user.email == user_2.email
    assert jsonable_encoder(user) == jsonable_encoder(user_2)
