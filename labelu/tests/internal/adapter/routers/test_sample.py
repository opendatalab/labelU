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
        data = [{"file_id": 1, "data": {}}]

        # run
        r = client.post(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples",
            headers=testuser_token_headers,
            json=data,
        )

        # check
        with db.begin():
            updated_task = crud_task.get(db=db, task_id=task.id)
        json = r.json()
        assert r.status_code == 201
        assert len(json["data"]["ids"]) == 1
        assert updated_task.status == "IMPORTED"

    def test_create_sample_task_status_not_draft(
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
        with db.begin():
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
                annotated_count=i,
            )
            for i in range(14)
        ]
        crud_sample.batch(
            db=db,
            samples=samples,
        )

        # run
        r = client.get(
            f"{settings.API_V1_STR}/tasks/{task.id}/samples?sort=annotated_count:desc",
            headers=testuser_token_headers,
            params={"after": 5, "size": 10},
        )

        # check
        json = r.json()
        assert r.status_code == 200
        assert len(json["data"]) == 9
        assert json["data"][0]["id"] == 14
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
            f"{settings.API_V1_STR}/tasks/{task.id}/samples?sort",
            headers=testuser_token_headers,
            params={"page": 0, "size": 10},
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
        task = crud_task.create(
            db=db,
            task=Task(
                name="name",
                description="description",
                tips="tips",
                config='{"tools":[{"tool":"rectTool","config":{"isShowCursor":false,"showConfirm":false,"skipWhileNoDependencies":false,"drawOutsideTarget":false,"copyBackwardResult":false,"minWidth":1,"attributeConfigurable":true,"textConfigurable":true,"textCheckType":4,"customFormat":"","attributes":[{"key":"rectTool","value":"rectTool"}]}},{"tool":"pointTool","config":{"upperLimit":10,"isShowCursor":false,"attributeConfigurable":true,"copyBackwardResult":false,"textConfigurable":true,"textCheckType":0,"customFormat":"","attributes":[{"key":"pointTool","value":"pointTool"}]}},{"tool":"polygonTool","config":{"isShowCursor":false,"lineType":0,"lineColor":0,"drawOutsideTarget":false,"edgeAdsorption":true,"copyBackwardResult":false,"attributeConfigurable":true,"textConfigurable":true,"textCheckType":0,"customFormat":"","attributes":[{"key":"polygonTool","value":"polygonTool"}],"lowerLimitPointNum":"4","upperLimitPointNum":100}},{"tool":"lineTool","config":{"isShowCursor":false,"lineType":0,"lineColor":1,"edgeAdsorption":true,"outOfTarget":true,"copyBackwardResult":false,"attributeConfigurable":true,"textConfigurable":true,"textCheckType":4,"customFormat":"^[\\\\s\\\\S]{1,3}$","lowerLimitPointNum":4,"upperLimitPointNum":"","attributes":[{"key":"lineTool","value":"lineTool"}]}},{"tool":"tagTool"},{"tool":"textTool"}],"tagList":[{"key":"类别1","value":"class1","isMulti":true,"subSelected":[{"key":"选项1","value":"option1","isDefault":true},{"key":"选项2","value":"option2","isDefault":false}]},{"key":"类别2","value":"class2","isMulti":true,"subSelected":[{"key":"a选项1","value":"aoption1","isDefault":true},{"key":"a选项2","value":"aoption2","isDefault":false}]}],"attributes":[{"key":"RT","value":"RT"}],"textConfig":[{"label":"我的描述","key":"描述的关键","required":true,"default":"","maxLength":200},{"label":"我的描述1","key":"描述的关键1","required":true,"default":"","maxLength":200}],"fileInfo":{"type":"img","list":[{"id":1,"url":"/src/img/example/bear6.webp","result":"[]"}]},"commonAttributeConfigurable":true}',
                created_by=0,
                updated_by=0,
            ),
        )
        samples = crud_sample.batch(
            db=db,
            samples=[
                TaskSample(
                    task_id=1,
                    file_id=1,
                    created_by=current_user.id,
                    updated_by=current_user.id,
                    data='{"result": "{\\"width\\":1256,\\"height\\":647,\\"valid\\":true,\\"rotate\\":0,\\"rectTool\\":{\\"toolName\\":\\"rectTool\\",\\"result\\":[{\\"x\\":76.7636304422194,\\"y\\":86.75077939093666,\\"width\\":156.47058823529457,\\"height\\":86.47058823529437,\\"label\\":\\"RT\\",\\"valid\\":true,\\"isVisible\\":true,\\"id\\":\\"J3eK0yr6\\",\\"sourceID\\":\\"\\",\\"textAttribute\\":\\"\\",\\"order\\":1},{\\"x\\":68.52833632457231,\\"y\\":288.5154852732902,\\"width\\":185.29411764705938,\\"height\\":115.29411764705917,\\"label\\":\\"rectTool\\",\\"valid\\":true,\\"isVisible\\":true,\\"id\\":\\"wDIMAnat\\",\\"sourceID\\":\\"\\",\\"textAttribute\\":\\"\\",\\"order\\":2}]},\\"pointTool\\":{\\"toolName\\":\\"pointTool\\",\\"result\\":[{\\"x\\":64.41068926574877,\\"y\\":543.8096029203498,\\"isVisible\\":true,\\"label\\":\\"无标签\\",\\"valid\\":true,\\"id\\":\\"FRejHry3\\",\\"textAttribute\\":\\"\\",\\"order\\":3},{\\"x\\":257.94010103045525,\\"y\\":552.0448970379969,\\"isVisible\\":true,\\"label\\":\\"pointTool\\",\\"valid\\":true,\\"id\\":\\"Hzj1lxHB\\",\\"textAttribute\\":\\"\\",\\"order\\":4}]},\\"polygonTool\\":{\\"toolName\\":\\"polygonTool\\",\\"result\\":[{\\"id\\":\\"YBVRgJYy\\",\\"valid\\":true,\\"isVisible\\":true,\\"textAttribute\\":\\"\\",\\"points\\":[{\\"x\\":517.3518657363384,\\"y\\":78.51548527328956},{\\"x\\":472.05774808927936,\\"y\\":247.33901468505476},{\\"x\\":859.1165716186923,\\"y\\":284.3978382144666},{\\"x\\":978.528336324575,\\"y\\":144.39783821446622},{\\"x\\":686.1753951481036,\\"y\\":49.691955861524775}],\\"label\\":\\"RT\\",\\"order\\":5},{\\"id\\":\\"miH6P16a\\",\\"valid\\":true,\\"isVisible\\":true,\\"textAttribute\\":\\"\\",\\"points\\":[{\\"x\\":550.2930422069267,\\"y\\":399.6919558615258},{\\"x\\":521.4695127951619,\\"y\\":556.1625440968204},{\\"x\\":735.587159853986,\\"y\\":552.0448970379969},{\\"x\\":842.6459833833981,\\"y\\":440.8684264497612},{\\"x\\":764.4106892657508,\\"y\\":395.57430880270226},{\\"x\\":616.1753951481033,\\"y\\":374.9860735085845}],\\"label\\":\\"polygonTool\\",\\"order\\":6}]},\\"lineTool\\":{\\"toolName\\":\\"lineTool\\",\\"result\\":[{\\"points\\":[{\\"x\\":970.2930422069279,\\"y\\":57.92724997917186,\\"id\\":\\"OIuogYeu\\"},{\\"x\\":1163.8224539716343,\\"y\\":107.33901468505437,\\"id\\":\\"ZpkyExOs\\"},{\\"x\\":1097.9401010304578,\\"y\\":144.39783821446625,\\"id\\":\\"A5pOdHao\\"},{\\"x\\":970.2930422069279,\\"y\\":132.0448970379956,\\"id\\":\\"20Lx7GQZ\\"}],\\"id\\":\\"3U3VY93T\\",\\"valid\\":true,\\"order\\":7,\\"isVisible\\":true,\\"label\\":\\"RT\\"},{\\"points\\":[{\\"x\\":1040.2930422069282,\\"y\\":284.3978382144667,\\"id\\":\\"1zdkvfsO\\"},{\\"x\\":1229.7048069128111,\\"y\\":284.3978382144667,\\"id\\":\\"L7E6NIDx\\"},{\\"x\\":1213.234218677517,\\"y\\":383.22136762623165,\\"id\\":\\"maDtUPWR\\"},{\\"x\\":1023.822453971634,\\"y\\":403.80960292034933,\\"id\\":\\"xCuDp9g0\\"}],\\"id\\":\\"VvfLXlii\\",\\"valid\\":true,\\"order\\":8,\\"isVisible\\":true,\\"label\\":\\"lineTool\\"}]},\\"tagTool\\":{\\"toolName\\":\\"tagTool\\",\\"result\\":[{\\"sourceID\\":\\"\\",\\"id\\":\\"5939weRA\\",\\"result\\":{\\"class1\\":\\"option1\\",\\"class2\\":\\"aoption1\\"}}]},\\"textTool\\":{\\"toolName\\":\\"textTool\\",\\"result\\":[{\\"id\\":\\"OhdGIhFX\\",\\"sourceID\\":\\"\\",\\"value\\":{\\"描述的关键\\":\\"我的描述\\"}},{\\"id\\":\\"1TN5jPTb\\",\\"sourceID\\":\\"\\",\\"value\\":{\\"描述的关键1\\":\\"我的描述1\\"}}]}}","urls": {"42": "http://localhost:8000/api/v1/tasks/attachment/upload/6/1/d9c34a05-screen.png"},"fileNames": {"42": ""}}',
                    annotated_count=1,
                    state="DONE",
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
