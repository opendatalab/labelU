from sqlalchemy.orm import Session
from pathlib import Path
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_pre_annotation
from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.adapter.persistence import crud_attachment
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.attachment import TaskAttachment
from labelu.internal.domain.models.pre_annotation import TaskPreAnnotation
from labelu.internal.domain.models.sample import TaskSample
from labelu.tests.utils.utils import empty_task_upload


class TestClassTaskPreAnnotationRouter:
    def test_create_pre_annotation_successful(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
            
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
        
        # prepare data
        empty_task_upload(task.id, "test.jsonl")
        with Path("labelu/tests/data/test.jsonl").open(mode="rb") as f:
            jsonl = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
            
        data = [{"file_id": jsonl.json()["data"]["id"]}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations",
            headers=testuser_token_headers,
            json=data,
        )

        json = r.json()
        assert r.status_code == 201
        assert len(json["data"]["ids"]) == 1
        
    def test_create_pre_annotation_sample_exists(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
            
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
        
        empty_task_upload(task.id, "test.jsonl")
        
        # prepare data
        with Path("labelu/tests/data/test.jsonl").open(mode="rb") as f:
            res = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
            
        data = [{"file_id": res.json()["data"]["id"]}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations",
            headers=testuser_token_headers,
            json=data,
        )
        
        empty_task_upload(task.id, "test.jsonl")
        
        with Path("labelu/tests/data/test.jsonl").open(mode="rb") as f:
            res = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
            
        data = [{"file_id": res.json()["data"]["id"]}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations",
            headers=testuser_token_headers,
            json=data,
        )

        assert r.status_code == 400

    def test_create_sample_task_not_found(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = [{"file_id": 1, "data": {}}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/0/pre_annotations",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        json = r.json()
        assert r.status_code == 404
        assert json["err_code"] == 50002

    def test_pre_annotation_list_by_page(
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
        
        empty_task_upload(task.id, "test.jsonl")
        
        with Path("labelu/tests/data/test.jsonl").open(mode="rb") as f:
            jsonl = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
        
        pre_annotations = [
            TaskPreAnnotation(
                task_id=task.id,
                file_id=jsonl.json()["data"]["id"],
                created_by=current_user.id,
                updated_by=current_user.id,
            )
            for i in range(14)
        ]
        
        crud_pre_annotation.batch(
            db=db,
            pre_annotations=pre_annotations,
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations",
            headers=testuser_token_headers,
            params={"page": 0, "size": 10},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 10
        assert json["data"][0]["id"] == 1
        assert json["meta_data"]["total"] == 14

    def test_pre_annotation_list_with_sample_name(
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
        
        empty_task_upload(task.id, "test.png")
        empty_task_upload(task.id, "test.jsonl")
        # upload sample file
        with Path("labelu/tests/data/test.png").open(mode="rb") as f:
            img = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
        # upload jsonl file
        with Path("labelu/tests/data/test.jsonl").open(mode="rb") as f:
            jsonl = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
        
        samples = [
            TaskSample(
                task_id=task.id,
                file_id=img.json()["data"]["id"],
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
            )
        ]
        crud_sample.batch(
            db=db,
            samples=samples,
        )
        
        pre_annotations = [
            TaskPreAnnotation(
                task_id=task.id,
                file_id=jsonl.json()["data"]["id"],
                sample_name=img.json()["data"]["filename"],
                created_by=current_user.id,
                updated_by=current_user.id,
            )
        ]
        crud_pre_annotation.batch(
            db=db,
            pre_annotations=pre_annotations,
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations?sample_name={img.json()['data']['filename']}",
            headers=testuser_token_headers,
            params={"page": 0},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert json["data"][0]["id"] == 1
        assert json["meta_data"]["total"] == 1

    def test_pre_annotation_list_with_sample_name_not_found(
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
        empty_task_upload(task.id, "test.png")
        # upload sample file
        with Path("labelu/tests/data/test.png").open(mode="rb") as f:
            img = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
        # upload jsonl file
        empty_task_upload(task.id, "test.jsonl")
        with Path("labelu/tests/data/test.jsonl").open(mode="rb") as f:
            jsonl = client.post(
                f"{settings.API_V1_STR}/tasks/{task.id}/attachments",
                headers=testuser_token_headers,
                files={"file": f},
            )
        
        samples = [
            TaskSample(
                task_id=task.id,
                file_id=img.json()["data"]["id"],
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
            )
        ]
        crud_sample.batch(
            db=db,
            samples=samples,
        )
        
        pre_annotations = [
            TaskPreAnnotation(
                task_id=task.id,
                file_id=jsonl.json()["data"]["id"],
                created_by=current_user.id,
                updated_by=current_user.id,
            )
        ]
        crud_pre_annotation.batch(
            db=db,
            pre_annotations=pre_annotations,
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations?sample_name=asdasd.png",
            headers=testuser_token_headers,
            params={"page": 0},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 0
    
    def test_pre_annotations_list_by_params_error(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{1}/pre_annotations",
            headers=testuser_token_headers,
            params={"after": 1, "before": 1, "page": 1, "size": 10},
        )

        # check
        assert r.status_code == 422

    def test_sample_list_by_sample_name_error(
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
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations?sample_name=",
            headers=testuser_token_headers,
            params={"page": 0, "size": 10},
        )

        # check
        assert r.status_code == 422

    def test_pre_annotation_get(
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
        pre_annotations = crud_pre_annotation.batch(
            db=db,
            pre_annotations=[
                TaskPreAnnotation(
                    task_id=task.id,
                    file_id=1,
                    created_by=current_user.id,
                    updated_by=current_user.id,
                )
            ],
        )
        
        assert pre_annotations[0] is not None

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations/{pre_annotations[0].id}",
            headers=testuser_token_headers,
        )

        # check
        assert r.status_code == 200

    def test_pre_annotation_delete(
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
        pre_annotations = crud_pre_annotation.batch(
            db=db,
            pre_annotations=[
                TaskPreAnnotation(
                    task_id=1,
                    file_id=1,
                    created_by=current_user.id,
                    updated_by=current_user.id,
                    data="{}",
                )
            ],
        )

        # run
        data = {"pre_annotation_ids": [pre_annotations[0].id]}
        r = client.request("delete",
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        assert r.status_code == 200

    def test_pre_annotations_delete_not_found(
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
        data = {"pre_annotation_ids": [1, 2]}
        r = client.request("delete",
            f"{settings.API_V1_STR}/tasks/{task.id}/pre_annotations",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        assert r.status_code == 200
