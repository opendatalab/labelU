from typing import Generator

import pytest
from fastapi.testclient import TestClient

from labelu.main import app
from labelu.internal.common.db import SessionLocal


@pytest.fixture(scope="session")
def db() -> Generator:
    yield SessionLocal()


@pytest.fixture(scope="module")
def client() -> Generator:
    with TestClient(app) as c:
        yield c
