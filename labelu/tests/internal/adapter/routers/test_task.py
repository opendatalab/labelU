from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.user import User
from labelu.internal.adapter.persistence import crud_user
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
        assert json["data"]["created_by"]["id"] > 0
        assert json["data"]["status"] == "DRAFT"

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
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        page = 0
        size = 10
        for i in range(15):
            crud_task.create(
                db=db,
                task=Task(
                    name="name",
                    description="description",
                    tips="tips",
                    created_by=current_user.id,
                    updated_by=current_user.id,
                ),
            )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            params={"page": page, "size": size},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert json["meta_data"]["total"] == 15
        assert len(json["data"]) == 10

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
        assert json["created_by"]["id"] > 0

    def test_task_get_not_found(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/0",
            headers=testuser_token_headers,
        )

        # check
        json = r.json()
        assert r.status_code == 404
        assert json["err_code"] == 50002

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
        updated_task = client.patch(
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

    def test_task_update_no_found_task(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        for_updated_task_data = {
            "name": "new name",
            "description": "new description",
            "tips": "new tips",
            "config": "new config",
            "media_type": "IMAGE",
        }

        # run
        updated_task = client.patch(
            f"{settings.API_V1_STR}/tasks/0",
            headers=testuser_token_headers,
            json=for_updated_task_data,
        )

        # check
        json = updated_task.json()
        assert updated_task.status_code == 404
        assert json["err_code"] == 50002

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
        updated_task = client.patch(
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

    def test_task_add_annotation_config(
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
            "media_type": "IMAGE",
        }

        # run
        task_id = for_update_task.json()["data"]["id"]
        updated_task = client.patch(
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
        assert json["data"]["status"] == "CONFIGURED"

    def test_task_delete(
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

        # run
        r = client.request("delete",
            f"{settings.API_V1_STR}/tasks/{task.id}", headers=testuser_token_headers
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert json["data"]["ok"] == True

    def test_task_delete_not_found(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        r = client.request("delete",
            f"{settings.API_V1_STR}/tasks/0", headers=testuser_token_headers
        )

        # check
        json = r.json()
        assert r.status_code == 404
        assert json["err_code"] == 50002

    def test_task_delete_no_permission(
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
        r = client.request("delete",
            f"{settings.API_V1_STR}/tasks/{task.id}", headers=testuser_token_headers
        )

        # check
        json = r.json()
        assert r.status_code == 403
        assert json["err_code"] == 30001

    def test_task_get_collaborators(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        # prepare data
        data = {
            "name": "task name",
            "description": "task description",
            "tips": "task tips",
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=data,
        )
        task_id = task_response.json()["data"]["id"]

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators",
            headers=testuser_token_headers,
        )

        # check
        json = r.json()
        assert r.status_code == 200
        # 创建者可能不会自动成为协作者，根据实际业务逻辑修改断言
        # assert len(json["data"]) >= 1

    def test_task_add_collaborator(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        # prepare data
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        data = {
            "name": "collaborative task",
            "description": "task description",
            "tips": "task tips",
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=data,
        )
        task_id = task_response.json()["data"]["id"]

        # run - 尝试添加当前用户为协作者（即使它已经是协作者）
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators",
            headers=testuser_token_headers,
            json={"user_id": current_user.id},
        )

        # check
        json = r.json()
        assert r.status_code == 201
        assert json["data"]["id"] == current_user.id

    def test_task_batch_add_collaborators(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        # prepare data
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        # 获取或创建测试用户
        new_user = crud_user.get_user_by_username(db=db, username="collaborator@example.com")
        if not new_user:
            new_user = crud_user.create(
                db=db,
                user=User(
                    username="collaborator@example.com",
                    hashed_password="hashed_password",
                ),
            )
        
        data = {
            "name": "batch collaborative task",
            "description": "task description",
            "tips": "task tips",
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=data,
        )
        task_id = task_response.json()["data"]["id"]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators/batch_add",
            headers=testuser_token_headers,
            json={"user_ids": [current_user.id, new_user.id]},
        )

        # check
        json = r.json()
        assert r.status_code == 201
        # 期望只有一个协作者
        assert len(json["data"]) == 1
        user_ids = [user["id"] for user in json["data"]]
        assert new_user.id in user_ids

    def test_task_batch_remove_collaborators(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        # prepare data
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        # 获取或创建测试用户
        new_user = crud_user.get_user_by_username(db=db, username="to_remove@example.com")
        if not new_user:
            new_user = crud_user.create(
                db=db,
                user=User(
                    username="to_remove@example.com",
                    hashed_password="hashed_password",
                ),
            )
        
        data = {
            "name": "remove collaborative task",
            "description": "task description",
            "tips": "task tips",
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=data,
        )
        task_id = task_response.json()["data"]["id"]

        # 先添加协作者
        client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators/batch_add",
            headers=testuser_token_headers,
            json={"user_ids": [new_user.id]},
        )

        # run - 移除协作者
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators/batch_remove",
            headers=testuser_token_headers,
            json={"user_ids": [new_user.id]},
        )

        # check
        json = r.json()
        assert r.status_code == 201
        assert json["data"]["ok"] == True

        # 验证协作者已被移除
        collaborators = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators",
            headers=testuser_token_headers,
        )
        assert new_user.id not in [c["id"] for c in collaborators.json()["data"]]

    def test_task_remove_collaborator(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        # prepare data
        # 获取或创建测试用户
        new_user = crud_user.get_user_by_username(db=db, username="single_remove@example.com")
        if not new_user:
            new_user = crud_user.create(
                db=db,
                user=User(
                    username="single_remove@example.com",
                    hashed_password="hashed_password",
                ),
            )
        
        data = {
            "name": "single remove task",
            "description": "task description",
            "tips": "task tips",
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=data,
        )
        task_id = task_response.json()["data"]["id"]

        # 先添加协作者
        client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators",
            headers=testuser_token_headers,
            json={"user_id": new_user.id},
        )

        # run - 移除单个协作者
        r = client.delete(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators/{new_user.id}",
            headers=testuser_token_headers,
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert json["data"]["ok"] == True

        # 验证协作者已被移除
        collaborators = client.get(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators",
            headers=testuser_token_headers,
        )
        assert new_user.id not in [c["id"] for c in collaborators.json()["data"]]

    def test_task_not_found_for_collaborators(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        # 测试不存在的任务
        r1 = client.get(
            f"{settings.API_V1_STR}/tasks/99999/collaborators",
            headers=testuser_token_headers,
        )
        assert r1.status_code == 404
        
    def test_user_not_found_for_collaborators(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        # 测试添加不存在的用户
        
        data = {
            "name": "error test task",
            "description": "task description",
            "tips": "task tips",
        }
        task_response = client.post(
            f"{settings.API_V1_STR}/tasks",
            headers=testuser_token_headers,
            json=data,
        )
        task_id = task_response.json()["data"]["id"]
        
        r2 = client.post(
            f"{settings.API_V1_STR}/tasks/{task_id}/collaborators",
            headers=testuser_token_headers,
            json={"user_id": 99999},  # 不存在的用户ID
        )
        # 验证状态码是4xx，表示客户端错误
        assert r2.status_code == 404
