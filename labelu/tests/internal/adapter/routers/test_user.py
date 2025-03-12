from datetime import timedelta

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.common.config import settings
from labelu.internal.common.security import AccessToken
from labelu.internal.common.security import get_password_hash
from labelu.internal.common.security import create_access_token

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
        crud_user.create(
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
        crud_user.create(
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

    def test_user_logout(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ):

        # run
        r = client.post(
            f"{settings.API_V1_STR}/users/logout", headers=testuser_token_headers
        )

        # check
        assert r.status_code == 200

    def test_user_token_error(self, client: TestClient, db: Session) -> None:

        # prepare data
        headers = {"Authorization": "Bearer token"}
        # run
        r = client.post(f"{settings.API_V1_STR}/users/logout", headers=headers)

        # check
        assert r.status_code == 403
        assert r.json()["err_code"] == 40003

    def test_cannot_not_found_token(self, client: TestClient, db: Session) -> None:

        # run
        r = client.post(f"{settings.API_V1_STR}/users/logout")

        # check
        assert r.status_code == 403
        assert r.json()["err_code"] == 30003

    def test_user_not_found(self, client: TestClient, db: Session) -> None:

        # prepare data
        username = random_username()
        access_token_expires = timedelta(minutes=settings.TOKEN_ACCESS_EXPIRE_MINUTES)
        access_token = create_access_token(
            token=AccessToken(id=-1, username=username),
            expires_delta=access_token_expires,
        )
        headers = {"Authorization": f"Bearer {access_token}"}
        # run
        r = client.post(f"{settings.API_V1_STR}/users/logout", headers=headers)

        # check
        assert r.status_code == 401
        assert r.json()["err_code"] == 40002
