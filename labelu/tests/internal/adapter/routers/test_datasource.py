from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from labelu.internal.common.config import settings
from labelu.internal.common.db import begin_transaction
from labelu.internal.domain.models.data_source import DataSource
from labelu.internal.adapter.persistence import crud_datasource


class TestDataSourceIDOR:
    def _other_users_datasource(self, db: Session) -> DataSource:
        with begin_transaction(db):
            return crud_datasource.create(
                db=db,
                data_source=DataSource(
                    name="victim-ds",
                    type="S3",
                    endpoint="https://8.8.8.8",
                    bucket="victim-bucket",
                    created_by=999,
                    updated_by=999,
                ),
            )

    def test_get_others_datasource_forbidden(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        ds = self._other_users_datasource(db)
        r = client.get(
            f"{settings.API_V1_STR}/datasources/{ds.id}",
            headers=testuser_token_headers,
        )
        assert r.status_code == 403

    def test_update_others_datasource_forbidden(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        ds = self._other_users_datasource(db)
        r = client.patch(
            f"{settings.API_V1_STR}/datasources/{ds.id}",
            headers=testuser_token_headers,
            json={"name": "hijacked"},
        )
        assert r.status_code == 403

    def test_delete_others_datasource_forbidden(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        ds = self._other_users_datasource(db)
        r = client.request(
            "delete",
            f"{settings.API_V1_STR}/datasources/{ds.id}",
            headers=testuser_token_headers,
        )
        assert r.status_code == 403

    def test_list_objects_others_datasource_forbidden(
        self, client: TestClient, testuser_token_headers: dict, db: Session
    ) -> None:
        ds = self._other_users_datasource(db)
        # must be denied before any S3 request is made with the victim's creds
        r = client.get(
            f"{settings.API_V1_STR}/datasources/{ds.id}/objects",
            headers=testuser_token_headers,
        )
        assert r.status_code == 403
