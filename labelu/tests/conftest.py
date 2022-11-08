import pytest
from typing import Dict, Generator

from fastapi.testclient import TestClient

from labelu.main import app
from labelu.internal.common.config import settings
from labelu.internal.common.db import SessionLocal
from labelu.internal.common.security import get_password_hash
from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user

TEST_USERNAME = "test@example.com"
TEST_USER_PASSWORD = "test"


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def testuser_token_headers(client: TestClient) -> Dict[str, str]:
    init_db()
    return get_testuser_token_headers(client)


def init_db() -> None:
    db = SessionLocal()
    user = crud_user.get_user_by_username(db, username=TEST_USERNAME)
    if not user:
        user_in = User(
            username=TEST_USERNAME,
            hashed_password=get_password_hash(TEST_USER_PASSWORD),
        )
        user = crud_user.create_user(db, user=user_in)


def get_testuser_token_headers(client: TestClient) -> Dict[str, str]:
    data = {
        "username": TEST_USERNAME,
        "password": TEST_USER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/users/login", json=data)
    token = r.json()["data"]["token"]
    headers = {"Authorization": f"{token}"}
    return headers
