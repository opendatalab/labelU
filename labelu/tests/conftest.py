import pytest
from typing import Dict, Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from labelu.main import app
from labelu.internal.common.config import settings
from labelu.internal.common.db import Base
from labelu.internal.common.db import begin_transaction
from labelu.internal.common.db import get_db
from labelu.internal.common.security import get_password_hash
from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user

TEST_USERNAME = "test@example.com"
TEST_USER_PASSWORD = "test@123"


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
)
TestingSessionLocal = sessionmaker(autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


def override_get_db():
    db = None
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True, scope="session")
def db() -> Generator:
    db = None
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        if db is not None:
            db.close()


@pytest.fixture(autouse=True)
def run_around_tests(db: Session):
    init_db()
    yield
    # Release any autobegin transaction on the session-scoped fixture so SQLite
    # teardown and TestClient requests do not deadlock.
    db.rollback()
    cleanup = None
    try:
        cleanup = TestingSessionLocal()
        meta = Base.metadata
        with begin_transaction(cleanup):
            for table in reversed(meta.sorted_tables):
                if table.key != "user":
                    cleanup.execute(table.delete())
    finally:
        if cleanup is not None:
            cleanup.close()


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
    db = None
    try:
        db = TestingSessionLocal()
        with begin_transaction(db):
            user = crud_user.get_user_by_username(db, username=TEST_USERNAME)
            if not user:
                user_in = User(
                    username=TEST_USERNAME,
                    hashed_password=get_password_hash(TEST_USER_PASSWORD),
                )
                user = crud_user.create(db=db, user=user_in)
    finally:
        if db is not None:
            db.close()
