from pathlib import Path

from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.domain.models.task import Task
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_attachment


class TestClassTaskAttachmentRouter:
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
                f"{settings.API_V1_STR}/tasks/{task_id}/attachments",
                headers=testuser_token_headers,
                files={"file": ("test.png", f, "image/png")},
            )

        # check
        json = new_res.json()
        assert new_res.status_code == 201
        assert settings.HOST in json["data"]["url"]

        parts = json["data"]["url"].split("/")[-3:]
        assert Path(f"{settings.MEDIA_ROOT}").joinpath("/".join(parts)).exists()
        parts[-1] = parts[-1][:8] + "-test-thumbnail.png"
        assert Path(f"{settings.MEDIA_ROOT}").joinpath("/".join(parts)).exists()

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
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )

        # check
        assert new_res.status_code == 500
        assert new_res.json()["err_code"] == 50001

    def test_upload_file_not_image(
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
        with Path("labelu/tests/data/test.txt").open(mode="rb") as f:
            new_res = client.post(
                f"{settings.API_V1_STR}/tasks/{task_id}/attachments",
                headers=testuser_token_headers,
                files={"file": ("test.txt", f, "plain/text")},
            )

        # check
        json = new_res.json()
        assert new_res.status_code == 201
        assert settings.HOST in json["data"]["url"]

        parts = json["data"]["url"].split("/")[-3:]
        assert Path(f"{settings.MEDIA_ROOT}").joinpath("/".join(parts)).exists()
        parts[-1] = parts[-1][:8] + "-test-thumbnail.txt"
        assert not Path(f"{settings.MEDIA_ROOT}").joinpath("/".join(parts)).exists()

    def test_upload_file_when_task_not_found(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        with Path("labelu/tests/data/test.png").open(mode="rb") as f:
            new_res = client.post(
                f"{settings.API_V1_STR}/tasks/0/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )

        # check
        assert new_res.status_code == 404
        assert new_res.json()["err_code"] == 50002

    def test_download_file_successful(
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
            attachment = client.post(
                f"{settings.API_V1_STR}/tasks/{task_id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
        url = attachment.json()["data"]["url"]

        # run
        r = client.get(
            url,
            headers=testuser_token_headers,
        )

        # check
        assert r.status_code == 200

    def test_download_file_not_found(
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
        r = client.get(
            url=f"{settings.SCHEME}://{settings.HOST}:{settings.PORT}{settings.API_V1_STR}/tasks/attachment/upload/1/0",
            headers=testuser_token_headers,
        )

        # check
        assert r.status_code == 404
        assert r.json()["err_code"] == 51001

    def test_task_delete_task_file(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        task = crud_task.create(
            db=db,
            task=Task(
                name="name",
                description="description",
                tips="tips",
                created_by=current_user.id,
                updated_by=current_user.id,
            ),
        )
        # upload file
        with Path("labelu/tests/data/test.png").open(mode="rb") as f:
            attachment = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
        attachment_id = attachment.json()["data"]["id"]
        attachment_path = attachment.json()["data"]["url"]

        # run
        data = {"attachment_ids": [attachment_id]}
        r = client.delete(
            f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        deleted = crud_attachment.get(db=db, attachment_id=attachment_id)
        file_full_path = Path(settings.MEDIA_ROOT).joinpath(attachment_path)
        assert r.status_code == 200
        assert not deleted
        assert not file_full_path.exists()

    def test_task_delete_task_file_not_found_task(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        data = {"attachment_ids": [1]}
        r = client.delete(
            f"{settings.API_V1_STR}/tasks/0/attachments",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        assert r.status_code == 404
        assert r.json()["err_code"] == 51001

    def test_task_delete_task_file_not_owner(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        task = crud_task.create(
            db=db,
            task=Task(
                name="name",
                description="description",
                tips="tips",
                created_by=0,
                updated_by=0,
            ),
        )

        # run
        data = {"attachment_ids": [1]}
        r = client.delete(
            f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        assert r.status_code == 403
        assert r.json()["err_code"] == 30001
