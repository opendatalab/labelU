from pathlib import Path

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task import TaskFile
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.adapter.persistence import crud_task


class TestClassTaskRouter:
    def test_create_annotation(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = {
            "skipped": False,
            "result_count": 2,
            "results": "[{},{}]",
        }

        # run
        r = client.post(
            f"{settings.API_V1_STR}/annotations?task_file_id=0",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        assert r.status_code == 201

    def test_annotation_get(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        r = client.get(
            f"{settings.API_V1_STR}/annotations?task_file_id=0",
            headers=testuser_token_headers,
        )

        # check
        assert r.status_code == 200

    def test_annotation_update(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = {
            "skipped": False,
            "result_count": 2,
            "results": "[{},{}]",
        }

        # run
        updated_task = client.put(
            f"{settings.API_V1_STR}/annotations/0",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        assert updated_task.status_code == 200

    def test_task_delete(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        r = client.delete(
            f"{settings.API_V1_STR}/annotations/0", headers=testuser_token_headers
        )

        # check
        json = r.json()
        assert r.status_code == 200
