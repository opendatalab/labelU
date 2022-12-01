from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.sample import TaskSample


class TestClassTaskSampleRouter:
    def test_create_sample_successful(
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
        data = [{"attachement_ids": [1], "data": {}}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        db.commit()
        updated_task = crud_task.get(db=db, task_id=task.id)
        json = r.json()
        assert r.status_code == 201
        assert len(json["data"]["ids"]) == 1

    def test_create_sample_task_not_found(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = [{"attachement_ids": [1], "data": {}}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/0/samples",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        json = r.json()
        assert r.status_code == 404
        assert json["err_code"] == 50002

    def test_sample_list_by_page(
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
                created_by=0,
                updated_by=0,
            ),
        )
        samples = [
            TaskSample(
                task_id=1,
                task_attachment_ids="[1]",
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
            )
            for i in range(14)
        ]
        crud_sample.batch(
            db=db,
            samples=samples,
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            params={"pageNo": 0, "pageSize": 10},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 10
        assert json["data"][0]["id"] == 1
        assert json["meta_data"]["total"] == 14

    def test_sample_list_by_before(
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
                created_by=0,
                updated_by=0,
            ),
        )
        samples = [
            TaskSample(
                task_id=1,
                task_attachment_ids="[1]",
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
            )
            for i in range(14)
        ]
        crud_sample.batch(
            db=db,
            samples=samples,
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            params={"before": 5, "pageSize": 10},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 4
        assert json["data"][0]["id"] == 1
        assert json["data"][3]["id"] == 4
        assert json["meta_data"]["total"] == 14

    def test_sample_list_by_after(
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
                created_by=0,
                updated_by=0,
            ),
        )
        samples = [
            TaskSample(
                task_id=1,
                task_attachment_ids="[1]",
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
            )
            for i in range(14)
        ]
        crud_sample.batch(
            db=db,
            samples=samples,
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            params={"after": 5, "pageSize": 10},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 9
        assert json["data"][0]["id"] == 6
        assert json["data"][8]["id"] == 14
        assert json["meta_data"]["total"] == 14

    def test_sample_list_by_params_error(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{1}/samples",
            headers=testuser_token_headers,
            params={"after": 1, "before": 1, "pageNo": 1, "pageSize": 10},
        )

        # check
        assert r.status_code == 422

    def test_sample_get(
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
                created_by=0,
                updated_by=0,
            ),
        )
        samples = crud_sample.batch(
            db=db,
            samples=[
                TaskSample(
                    task_id=1,
                    task_attachment_ids="[1]",
                    created_by=current_user.id,
                    updated_by=current_user.id,
                    data="{}",
                )
            ],
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/{samples[0].id}",
            headers=testuser_token_headers,
        )

        # check
        json = r.json()
        assert r.status_code == 200

    def test_sample_get_not_found(
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
                created_by=0,
                updated_by=0,
            ),
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/0",
            headers=testuser_token_headers,
        )

        # check
        json = r.json()
        assert r.status_code == 404
        assert json["err_code"] == 55001

    def test_sample_patch(
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
                created_by=0,
                updated_by=0,
            ),
        )
        samples = crud_sample.batch(
            db=db,
            samples=[
                TaskSample(
                    task_id=1,
                    task_attachment_ids="[1]",
                    created_by=current_user.id,
                    updated_by=current_user.id,
                    data="{}",
                )
            ],
        )

        # run
        data = {
            "data": {"key1": "value1", "key2": [{"key3": "value3"}]},
            "annotated_count": 1,
        }
        r = client.patch(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/{samples[0].id}",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert json["data"]["state"] == "DONE"

    def test_sample_patch_skip(
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
                created_by=0,
                updated_by=0,
            ),
        )
        samples = crud_sample.batch(
            db=db,
            samples=[
                TaskSample(
                    task_id=1,
                    task_attachment_ids="[1]",
                    created_by=current_user.id,
                    updated_by=current_user.id,
                    data="{}",
                )
            ],
        )

        # run
        data = {"state": "SKIPPED"}
        r = client.patch(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/{samples[0].id}",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert json["data"]["state"] == "SKIPPED"

    def test_sample_patch_not_found(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        data = {"state": "SKIPPED"}
        r = client.patch(
            f"{settings.API_V1_STR}/tasks/0/samples/0",
            headers=testuser_token_headers,
            json=data,
        )
        # check
        json = r.json()
        assert r.status_code == 404
        assert json["err_code"] == 55001

    def test_sample_delete(
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
                created_by=0,
                updated_by=0,
            ),
        )
        samples = crud_sample.batch(
            db=db,
            samples=[
                TaskSample(
                    task_id=1,
                    task_attachment_ids="[1]",
                    created_by=current_user.id,
                    updated_by=current_user.id,
                    data="{}",
                )
            ],
        )

        # run
        data = {"sample_ids": [samples[0].id]}
        r = client.delete(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        assert r.status_code == 200

    def test_sample_delete_not_found(
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
        data = {"sample_ids": [1, 2]}
        r = client.delete(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        assert r.status_code == 200

    def test_export_sample(
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
                created_by=0,
                updated_by=0,
            ),
        )
        samples = crud_sample.batch(
            db=db,
            samples=[
                TaskSample(
                    task_id=1,
                    task_attachment_ids="[1]",
                    created_by=current_user.id,
                    updated_by=current_user.id,
                    data='{"key1": "value1", "key2": [{"key3": "value3"}]}',
                    annotated_count=1,
                )
            ],
        )

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/export?export_type=JSON",
            headers=testuser_token_headers,
            json={"sample_ids": [1]},
        )

        # check
        assert r.status_code == 200
