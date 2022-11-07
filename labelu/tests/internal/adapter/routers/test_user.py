from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.common.security import get_password_hash
from labelu.internal.application.response.error_code import ErrorCode

from labelu.tests.utils.utils import random_username
from labelu.tests.utils.utils import random_lower_string


class TestClassUserRouter:
    def test_user_signup_successful(self, client: TestClient, db: Session):

        # prepare data
        username = random_username()
        password = random_lower_string()
        data = {"username": username, "password": password}

        # run
        r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)

        # check
        assert r.status_code == 201
        created_user = r.json()
        user = crud_user.get_user_by_username(db, username=username)
        assert user
        assert user.username == created_user["data"]["username"]

    def test_create_user_existing_username(self, client: TestClient, db: Session):
        # prepare data
        username = random_username()
        password = random_lower_string()
        data = {"username": username, "password": password}
        crud_user.create_user(
            db=db,
            user=User(username=username, hashed_password=get_password_hash(password)),
        )

        # run
        r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)

        # check
        created_user = r.json()
        assert r.status_code == 400
        assert created_user["err_code"] == 40001

    def test_user_login_sucessful(self, client: TestClient, db: Session):
        # prepare data
        username = random_username()
        password = random_lower_string()
        data = {"username": username, "password": password}
        crud_user.create_user(
            db=db,
            user=User(username=username, hashed_password=get_password_hash(password)),
        )

        # run
        r = client.post(f"{settings.API_V1_STR}/users/login", json=data)

        # check
        assert r.status_code == 200
        assert r.json()["data"]["token"].startswith(settings.TOKEN_TYPE)

    def test_user_login_cannot_find_user(self, client: TestClient, db: Session):
        # prepare data
        username = random_username()
        password = random_lower_string()
        data = {"username": username, "password": password}

        # run
        r = client.post(f"{settings.API_V1_STR}/users/login", json=data)

        # check
        user = r.json()
        assert r.status_code == 401
        assert user["err_code"] == 40000

    def test_user_logout(self, client: TestClient, db: Session):
        # prepare data
        headers = {"Authorization": f"Bearer token"}

        # run
        r = client.post(f"{settings.API_V1_STR}/users/logout", headers=headers)

        # check
        assert r.status_code == 200
