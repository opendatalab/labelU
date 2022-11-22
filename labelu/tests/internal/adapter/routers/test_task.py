from pathlib import Path

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.domain.models.task import Task
from labelu.internal.adapter.persistence import crud_task


class TestClassTaskRouter:
    def test_create_task_successful(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
        }

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks", headers=testuser_token_headers, json=data
        )

        # check
        json = r.json()
        assert r.status_code == 201
        assert json["data"]["id"] > 0

    def test_create_task_no_authentication(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
        }

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks", headers=testuser_token_headers, json=data
        )

        # check
        assert r.status_code == 201

    def test_task_list(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        page = 0
        size = 10

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            params={"page": page, "size": size},
        )

        # check
        assert r.status_code == 200

    def test_task_get(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
            "config": "config",
            "media_type": "IMAGE",
        }
        task = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=data,
        )

        # run
        task_id = task.json()["data"]["id"]
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=testuser_token_headers,
        )

        # check
        json = r.json()["data"]
        assert r.status_code == 200
        assert json["name"] == "task name"

    def test_task_update(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        for_update_task_data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
            "config": "config",
            "media_type": "IMAGE",
        }
        for_update_task = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=for_update_task_data,
        )
        for_updated_task_data = {
            "name": "new name",
            "description": "new description",
            "tips": "new tips",
            "config": "new config",
            "media_type": "IMAGE",
        }

        # run
        task_id = for_update_task.json()["data"]["id"]
        updated_task = client.put(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=testuser_token_headers,
            json=for_updated_task_data,
        )

        # check
        json = updated_task.json()
        assert json["data"]["name"] == "new name"
        assert json["data"]["description"] == "new description"
        assert json["data"]["tips"] == "new tips"
        assert json["data"]["config"] == "new config"
        assert json["data"]["media_type"] == "IMAGE"

    def test_task_update_no_config(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        for_update_task_data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
        }
        for_update_task = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=for_update_task_data,
        )
        for_updated_task_data = {
            "name": "new name",
            "description": "new description",
            "tips": "new tips",
            "config": "new config",
        }

        # run
        task_id = for_update_task.json()["data"]["id"]
        updated_task = client.put(
            f"{settings.API_V1_STR}/tasks/{task_id}",
            headers=testuser_token_headers,
            json=for_updated_task_data,
        )

        # check
        json = updated_task.json()
        assert json["data"]["name"] == "new name"
        assert json["data"]["description"] == "new description"
        assert json["data"]["tips"] == "new tips"
        assert json["data"]["config"] == None
        assert json["data"]["media_type"] == None

    def test_upload_file_successful(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
        }
        task = client.post(
            f"{settings.API_V1_STR}/tasks", headers=testuser_token_headers, json=data
        )
        task_id = task.json()["data"]["id"]

        # run
        with Path("labelu/tests/data/test.png").open(mode="rb") as f:
            new_res = client.post(
                f"{settings.API_V1_STR}/tasks/{task_id}/upload",
                headers=testuser_token_headers,
                files={"file": f},
            )

        # check
        assert new_res.status_code == 201
        assert f"{settings.UPLOAD_DIR}/{task_id}" in new_res.json()["data"]["filename"]
        assert "test.png" in new_res.json()["data"]["filename"]

    def test_upload_file_when_task_finished(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        task = crud_task.create(
            db=db,
            task=Task(
                name="name",
                description="description",
                tips="tips",
                config="config",
                media_type="IMAGE",
                status="FINISHED",
            ),
        )

        # run
        with Path("labelu/tests/data/test.png").open(mode="rb") as f:
            new_res = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/upload",
                headers=testuser_token_headers,
                files={"file": f},
            )

        # check
        assert new_res.status_code == 500
        assert new_res.json()["err_code"] == 50001

    def test_update_successful(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
        }
        task = client.post(
            f"{settings.API_V1_STR}/tasks", headers=testuser_token_headers, json=data
        )
        task_id = task.json()["data"]["id"]
        update_data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
            "config": "{}",
        }

        # run
        r = client.put(
            f"{settings.API_V1_STR}/tasks/1",
            headers=testuser_token_headers,
            json=update_data,
        )
        # check
        assert r.status_code == 200

    def test_list_upload_file_successful(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        page = 0
        size = 10
        data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
        }
        task = client.post(
            f"{settings.API_V1_STR}/tasks", headers=testuser_token_headers, json=data
        )
        task_id = task.json()["data"]["id"]

        # upload file
        with Path("labelu/tests/data/test.png").open(mode="rb") as f:
            new_res = client.post(
                f"{settings.API_V1_STR}/tasks/{task_id}/upload",
                headers=testuser_token_headers,
                files={"file": f},
            )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}/uploads",
            headers=testuser_token_headers,
            params={"page": page, "size": size},
        )

        # check
        assert r.status_code == 200
        assert len(r.json()["data"]) > 0

    def test_get_upload_file_successful(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
        }
        task = client.post(
            f"{settings.API_V1_STR}/tasks", headers=testuser_token_headers, json=data
        )
        task_id = task.json()["data"]["id"]

        # upload file
        with Path("labelu/tests/data/test.png").open(mode="rb") as f:
            task_file = client.post(
                f"{settings.API_V1_STR}/tasks/{task_id}/upload",
                headers=testuser_token_headers,
                files={"file": f},
            )
        task_file_id = task_file.json()["data"]["id"]

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}/uploads/{task_file_id}",
            headers=testuser_token_headers,
        )

        # check
        assert r.status_code == 200
