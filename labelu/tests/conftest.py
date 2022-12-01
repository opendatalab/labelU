import pytest
from typing import Dict, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from labelu.main import app
from labelu.internal.common.config import settings
from labelu.internal.common.db import Base
from labelu.internal.common.db import get_db
from labelu.internal.common.security import get_password_hash
from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user

TEST_USERNAME = "test@example.com"
TEST_USER_PASSWORD = "test@123"


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}, echo=True
)
TestingSessionLocal = sessionmaker(autocommit=True, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope="session")
def db() -> Generator:
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def run_around_tests():
    # Code that will run before your test, for example:
    print("start up")
    init_db()
    # A test function will be run at this point
    yield
    # Code that will run after your test, for example:
    print("tear down")
    try:
        db = TestingSessionLocal()
        meta = Base.metadata
        with db.begin():
            for table in reversed(meta.sorted_tables):
                if table.key != "user":
                    db.execute(table.delete())
    finally:
        db.close()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def testuser_token_headers(client: TestClient) -> Dict[str, str]:
    return get_testuser_token_headers(client)


def get_testuser_token_headers(client: TestClient) -> Dict[str, str]:
    data = {
        "username": TEST_USERNAME,
        "password": TEST_USER_PASSWORD,
    }
    r = client.post(f"{settings.API_V1_STR}/users/login", json=data)
    token = r.json()["data"]["token"]
    headers = {"Authorization": f"{token}"}
    return headers


def init_db() -> None:
    try:
        db = TestingSessionLocal()
        with db.begin():
            user = crud_user.get_user_by_username(db, username=TEST_USERNAME)
            if not user:
                user_in = User(
                    username=TEST_USERNAME,
                    hashed_password=get_password_hash(TEST_USER_PASSWORD),
                )
                user = crud_user.create(db=db, user=user_in)
    finally:
        db.close()
