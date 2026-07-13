import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Make the test suite hermetic: every run gets its own throwaway directory that
# holds BOTH the sqlite test DB and all uploaded media. Without this, tests
# wrote uploads into the developer's real appdirs data directory
# (~/Library/Application Support/labelu/media) and kept ``test.db`` in the cwd,
# so ``sqlite_sequence`` accumulated across runs and freshly minted task_ids
# collided with leftover ``upload/<task_id>/...`` files, intermittently failing
# uploads with a 400 "file already exists". The directory must be chosen at
# import time because the engine below is created at module import, before any
# pytest ``tmp_path``/``monkeypatch`` fixture could run. It is removed at the end
# of the session by the ``_hermetic_storage`` fixture.
_TEST_DATA_DIR = Path(tempfile.mkdtemp(prefix="labelu-test-"))

from labelu.internal.common.config import settings

# Redirect media storage into the isolated directory and drop the memoized
# storage backend so it resolves paths against the new MEDIA_ROOT.
settings.STORAGE_BACKEND = "local"
settings.MEDIA_ROOT = _TEST_DATA_DIR / "media"
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

from labelu.internal.common.storage import get_storage_backend

get_storage_backend.cache_clear()

from labelu.main import app
from labelu.internal.common.db import Base
from labelu.internal.common.db import begin_transaction
from labelu.internal.common.db import get_db
from labelu.internal.common.security import get_password_hash
from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user

TEST_USERNAME = "test@example.com"
TEST_USER_PASSWORD = "test@123"


SQLALCHEMY_DATABASE_URL = f"sqlite:///{_TEST_DATA_DIR / 'test.db'}"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False, "timeout": 30},
)
TestingSessionLocal = sessionmaker(autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)


@pytest.fixture(autouse=True, scope="session")
def _hermetic_storage() -> Generator:
    """Guarantee the isolated media root is active and clean it up afterwards.

    The redirect itself happens at import time (above); this fixture re-clears
    the storage-backend cache in case anything memoized it during collection and
    removes the throwaway directory (test DB + media) once the session ends.
    """
    get_storage_backend.cache_clear()
    try:
        yield
    finally:
        engine.dispose()
        get_storage_backend.cache_clear()
        shutil.rmtree(_TEST_DATA_DIR, ignore_errors=True)


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
        # Seed the test user at session scope so it exists before the
        # module-scoped ``testuser_token_headers`` fixture logs in. The
        # per-test ``run_around_tests`` cleanup preserves the ``user`` table, so
        # this single seed lasts the whole session. (Previously the user
        # survived only because ``test.db`` persisted in the cwd across runs.)
        init_db()
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
