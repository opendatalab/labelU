from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.common.db import begin_transaction
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.adapter.persistence import crud_export_job
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.sample import TaskSample


class TestClassTaskSampleRouter:
    def test_create_sample_successful(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        with begin_transaction(db):
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
        data = [{"file_id": 1, "data": {}}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        db.expire_all()
        updated_task = crud_task.get(db=db, task_id=task.id)
        json = r.json()
        assert r.status_code == 201
        assert len(json["data"]["ids"]) == 1
        assert updated_task.status == "IMPORTED"

    def test_create_sample_task_status_not_draft(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        with begin_transaction(db):
            task = crud_task.create(
                db=db,
                task=Task(
                    name="name",
                    description="description",
                    tips="tips",
                    created_by=0,
                    updated_by=0,
                    status="CONFIGURED",
                ),
            )
        data = [{"file_id": 1, "data": {}}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        db.expire_all()
        updated_task = crud_task.get(db=db, task_id=task.id)
        json = r.json()
        assert r.status_code == 201
        assert len(json["data"]["ids"]) == 1
        assert updated_task.status == "CONFIGURED"

    def test_create_sample_task_not_found(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        data = [{"file_id": 1, "data": {}}]

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
        with begin_transaction(db):
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
                file_id=12,
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
            )
            for i in range(14)
        ]
        with begin_transaction(db):
            crud_sample.batch(
                db=db,
                samples=samples,
            )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            params={"page": 0, "size": 10},
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
        with begin_transaction(db):
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
                file_id=1,
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
            )
            for i in range(14)
        ]
        with begin_transaction(db):
            crud_sample.batch(
                db=db,
                samples=samples,
            )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            params={"before": 13, "size": 10},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 10
        assert json["data"][0]["id"] == 3
        assert json["data"][-1]["id"] == 12
        assert json["meta_data"]["total"] == 14

    def test_sample_list_by_after(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        with begin_transaction(db):
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
                file_id=1,
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
            )
            for i in range(14)
        ]
        with begin_transaction(db):
            crud_sample.batch(
                db=db,
                samples=samples,
            )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            params={"after": 5, "size": 10},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 9
        assert json["data"][0]["id"] == 6
        assert json["data"][8]["id"] == 14
        assert json["meta_data"]["total"] == 14

    def test_sample_list_with_sort(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        with begin_transaction(db):
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
                task_id=task.id,
                file_id=1,
                created_by=current_user.id,
                updated_by=current_user.id,
                data="{}",
                annotated_count=i,
            )
            for i in range(14)
        ]
        with begin_transaction(db):
            crud_sample.batch(
                db=db,
                samples=samples,
            )

        # get actual sample IDs for assertions
        sample_ids = sorted([s.id for s in samples])
        after_id = sample_ids[4]  # 5th sample (index 4)

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            params={"sort": "annotated_count:desc", "after": after_id, "size": 10},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 9
        # first item should have highest annotated_count (sorted desc)
        assert json["data"][0]["annotated_count"] >= json["data"][1]["annotated_count"]
        assert json["meta_data"]["total"] == 14

    def test_sample_list_by_params_error(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{1}/samples",
            headers=testuser_token_headers,
            params={"after": 1, "before": 1, "page": 1, "size": 10},
        )

        # check
        assert r.status_code == 422

    def test_sample_list_by_sort_error(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        with begin_transaction(db):
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
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            params={"sort": "", "page": 0, "size": 10},
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
        with begin_transaction(db):
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
        with begin_transaction(db):
            samples = crud_sample.batch(
                db=db,
                samples=[
                    TaskSample(
                        task_id=task.id,
                        file_id=1,
                        created_by=current_user.id,
                        updated_by=current_user.id,
                        data="{}",
                    )
                ],
            )
        
        print(samples)

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
        with begin_transaction(db):
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
        with begin_transaction(db):
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
        with begin_transaction(db):
            samples = crud_sample.batch(
                db=db,
                samples=[
                    TaskSample(
                        task_id=1,
                        file_id=1,
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
        with begin_transaction(db):
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
        with begin_transaction(db):
            samples = crud_sample.batch(
                db=db,
                samples=[
                    TaskSample(
                        task_id=1,
                        file_id=1,
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

    def test_sample_patch_task_not_found(
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
        assert json["err_code"] == 50002

    def test_sample_patch_task_sample_not_found(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:

        # prepare data
        with begin_transaction(db):
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
        data = {"state": "SKIPPED"}
        r = client.patch(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/0",
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
        with begin_transaction(db):
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
        with begin_transaction(db):
            samples = crud_sample.batch(
                db=db,
                samples=[
                    TaskSample(
                        task_id=1,
                        file_id=1,
                        created_by=current_user.id,
                        updated_by=current_user.id,
                        data="{}",
                    )
                ],
            )

        # run
        data = {"sample_ids": [samples[0].id]}
        r = client.request("delete",
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
        with begin_transaction(db):
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
        r = client.request("delete",
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
        with begin_transaction(db):
            task = crud_task.create(
                db=db,
                task=Task(
                    name="name",
                    description="description",
                    tips="tips",
                    config='{"tools":[{"tool":"rectTool","config":{"isShowCursor":false,"showConfirm":false,"skipWhileNoDependencies":false,"drawOutsideTarget":false,"copyBackwardResult":false,"minWidth":1,"attributeConfigurable":true,"textConfigurable":true,"textCheckType":4,"customFormat":"","attributes":[{"key":"rectTool","value":"rectTool"}]}},{"tool":"pointTool","config":{"upperLimit":10,"isShowCursor":false,"attributeConfigurable":true,"copyBackwardResult":false,"textConfigurable":true,"textCheckType":0,"customFormat":"","attributes":[{"key":"pointTool","value":"pointTool"}]}},{"tool":"polygonTool","config":{"isShowCursor":false,"lineType":0,"lineColor":0,"drawOutsideTarget":false,"edgeAdsorption":true,"copyBackwardResult":false,"attributeConfigurable":true,"textConfigurable":true,"textCheckType":0,"customFormat":"","attributes":[{"key":"polygonTool","value":"polygonTool"}],"lowerLimitPointNum":"4","upperLimitPointNum":100}},{"tool":"lineTool","config":{"isShowCursor":false,"lineType":0,"lineColor":1,"edgeAdsorption":true,"outOfTarget":true,"copyBackwardResult":false,"attributeConfigurable":true,"textConfigurable":true,"textCheckType":4,"customFormat":"^[\s\S]{1,3}$","lowerLimitPointNum":4,"upperLimitPointNum":"","attributes":[{"key":"lineTool","value":"lineTool"}]}},{"tool":"tagTool"},{"tool":"textTool"}],"tagList":[{"key":"类别1","value":"class1","isMulti":true,"subSelected":[{"key":"选项1","value":"option1","isDefault":true},{"key":"选项2","value":"option2","isDefault":false}]},{"key":"类别2","value":"class2","isMulti":true,"subSelected":[{"key":"a选项1","value":"aoption1","isDefault":true},{"key":"a选项2","value":"aoption2","isDefault":false}]}],"attributes":[{"key":"RT","value":"RT"}],"textConfig":[{"label":"我的描述","key":"描述的关键","required":true,"default":"","maxLength":200},{"label":"我的描述1","key":"描述的关键1","required":true,"default":"","maxLength":200}],"fileInfo":{"type":"img","list":[{"id":1,"url":"/src/img/example/bear6.webp","result":"[]"}]},"commonAttributeConfigurable":true}',
                    created_by=0,
                    updated_by=0,
                ),
            )
            samples = crud_sample.batch(
                db=db,
                samples=[
                    TaskSample(
                        task_id=task.id,
                        file_id=1,
                        created_by=current_user.id,
                        updated_by=current_user.id,
                        data='{"result": "{\"width\":1256,\"height\":647,\"valid\":true,\"rotate\":0,\"rectTool\":{\"toolName\":\"rectTool\",\"result\":[{\"x\":76.7636304422194,\"y\":86.75077939093666,\"width\":156.47058823529457,\"height\":86.47058823529437,\"label\":\"RT\",\"valid\":true,\"isVisible\":true,\"id\":\"J3eK0yr6\",\"sourceID\":\"\",\"textAttribute\":\"\",\"order\":1}]}}","urls": {"42": "http://localhost:8000/api/v1/tasks/attachment/upload/6/1/d9c34a05-screen.png"},"fileNames": {"42": ""}}',
                        annotated_count=1,
                        state="DONE",
                    )
                ],
            )

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/export?export_type=JSON",
            headers=testuser_token_headers,
            json={"sample_ids": [samples[0].id]},
        )

        # check - async export returns job info
        assert r.status_code == 200
        data = r.json()
        assert "data" in data
        assert data["data"]["status"] == "PENDING"
        assert data["data"]["sample_count"] == 1
        assert "id" in data["data"]

    def test_export_includes_all_states(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        """Verify NEW, DONE, SKIPPED samples are all included in export job."""

        # prepare data
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        with begin_transaction(db):
            task = crud_task.create(
                db=db,
                task=Task(
                    name="name",
                    description="description",
                    tips="tips",
                    config='{"tools":[{"tool":"rectTool","config":{"attributes":[{"key":"RT","value":"RT"}]}}],"tagList":[],"attributes":[],"textConfig":[],"fileInfo":{"type":"img","list":[]},"commonAttributeConfigurable":true}',
                    created_by=0,
                    updated_by=0,
                ),
            )
            result_data = '{"result": "{\"width\":100,\"height\":100,\"valid\":true,\"rotate\":0,\"rectTool\":{\"toolName\":\"rectTool\",\"result\":[{\"x\":10,\"y\":10,\"width\":50,\"height\":50,\"label\":\"RT\",\"valid\":true,\"isVisible\":true,\"id\":\"test1\",\"order\":1}]}}"}'
            samples = crud_sample.batch(
                db=db,
                samples=[
                    TaskSample(
                        task_id=task.id,
                        file_id=1,
                        created_by=current_user.id,
                        updated_by=current_user.id,
                        data=result_data,
                        annotated_count=1,
                        state="DONE",
                    ),
                    TaskSample(
                        task_id=task.id,
                        file_id=1,
                        created_by=current_user.id,
                        updated_by=current_user.id,
                        data=result_data,
                        annotated_count=0,
                        state="NEW",
                    ),
                    TaskSample(
                        task_id=task.id,
                        file_id=1,
                        created_by=current_user.id,
                        updated_by=current_user.id,
                        data=result_data,
                        annotated_count=0,
                        state="SKIPPED",
                    ),
                ],
            )

        sample_ids = [s.id for s in samples]

        # run - create export job
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/export?export_type=JSON",
            headers=testuser_token_headers,
            json={"sample_ids": sample_ids},
        )

        # check - all 3 samples should be counted
        assert r.status_code == 200
        data = r.json()
        assert data["data"]["sample_count"] == 3


    def test_export_status_reports_skipped_count(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        current_user = crud_user.get_user_by_username(
            db=db, username="test@example.com"
        )
        with begin_transaction(db):
            task = crud_task.create(
                db=db,
                task=Task(
                    name="status task",
                    description="description",
                    tips="tips",
                    config='{"tools":[{"tool":"rectTool","config":{"attributes":[{"key":"RT","value":"RT"}]}}],"tagList":[],"attributes":[],"textConfig":[],"fileInfo":{"type":"img","list":[]},"commonAttributeConfigurable":true}',
                    created_by=0,
                    updated_by=0,
                ),
            )
            job = crud_export_job.create(
                db=db,
                task_id=task.id,
                user_id=current_user.id,
                export_type="JSON",
                sample_ids=[1, 2, 3],
            )
            crud_export_job.update_status(
                db=db,
                job=job,
                status="COMPLETED",
                processed_count=1,
                file_path="/tmp/result.json",
            )

        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples/export/{job.id}",
            headers=testuser_token_headers,
        )

        assert r.status_code == 200
        data = r.json()["data"]
        assert data["sample_count"] == 3
        assert data["processed_count"] == 1
        assert data["skipped_count"] == 2
        assert "warning_message" in data and data["warning_message"]
