from __future__ import annotations

from typing import List, Tuple, Optional

import boto3
from botocore.config import Config
from fastapi import status
from loguru import logger
from sqlalchemy.orm import Session

from labelu.internal.adapter.persistence import crud_datasource
from labelu.internal.application.command.datasource import (
    CreateDataSourceCommand,
    UpdateDataSourceCommand,
)
from labelu.internal.application.response.datasource import (
    DataSourceResponse,
    S3ObjectItem,
    S3ObjectListResponse,
)
from labelu.internal.common.crypto import decrypt_value, encrypt_value
from labelu.internal.common.db import begin_transaction
from labelu.internal.common.error_code import ErrorCode, LabelUException
from labelu.internal.domain.models.data_source import DataSource
from labelu.internal.domain.models.user import User


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif", ".gif"}


def _to_response(ds: DataSource) -> DataSourceResponse:
    return DataSourceResponse(
        id=ds.id,
        name=ds.name,
        type=ds.type,
        endpoint=ds.endpoint,
        region=ds.region,
        bucket=ds.bucket,
        prefix=ds.prefix or "",
        path_style=ds.path_style,
        use_ssl=ds.use_ssl,
        presign_expire_secs=ds.presign_expire_secs,
        created_by=ds.created_by,
        created_at=ds.created_at,
        updated_at=ds.updated_at,
    )


def _build_s3_client(ds: DataSource):
    """Create a boto3 S3 client from a DataSource's (decrypted) credentials."""
    ak = decrypt_value(ds.access_key_id) if ds.access_key_id else None
    sk = decrypt_value(ds.secret_access_key) if ds.secret_access_key else None
    kwargs = {}
    if ds.region:
        kwargs["region_name"] = ds.region
    kwargs["config"] = Config(
        s3={"addressing_style": "path" if ds.path_style else "auto"}
    )
    return boto3.client(
        "s3",
        endpoint_url=ds.endpoint or None,
        aws_access_key_id=ak,
        aws_secret_access_key=sk,
        use_ssl=ds.use_ssl,
        **kwargs,
    )


def get_presigned_url(ds: DataSource, key: str, expires_in: Optional[int] = None) -> str:
    """Generate a presigned read URL for a given object key using the data source credentials."""
    client = _build_s3_client(ds)
    return client.generate_presigned_url(
        ClientMethod="get_object",
        Params={"Bucket": ds.bucket, "Key": key},
        ExpiresIn=expires_in or ds.presign_expire_secs or 3600,
    )


# ── CRUD ──────────────────────────────────────────────────────────────

async def create(
    db: Session, cmd: CreateDataSourceCommand, current_user: User
) -> DataSourceResponse:
    ds = DataSource(
        name=cmd.name,
        type=cmd.type,
        endpoint=cmd.endpoint,
        region=cmd.region,
        bucket=cmd.bucket,
        prefix=cmd.prefix,
        access_key_id=encrypt_value(cmd.access_key_id),
        secret_access_key=encrypt_value(cmd.secret_access_key),
        path_style=cmd.path_style,
        use_ssl=cmd.use_ssl,
        presign_expire_secs=cmd.presign_expire_secs,
        created_by=current_user.id,
        updated_by=current_user.id,
    )
    with begin_transaction(db):
        ds = crud_datasource.create(db=db, data_source=ds)
    return _to_response(ds)


async def list_by(
    db: Session, current_user: User, page: int = 0, size: int = 100
) -> Tuple[List[DataSourceResponse], int]:
    items, total = crud_datasource.list_by_user(
        db=db, user_id=current_user.id, page=page, size=size
    )
    return [_to_response(ds) for ds in items], total


async def get(db: Session, ds_id: int) -> DataSourceResponse:
    ds = crud_datasource.get(db=db, ds_id=ds_id)
    if not ds:
        raise LabelUException(
            code=ErrorCode.CODE_61000_NO_DATA,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    return _to_response(ds)


async def update(
    db: Session, ds_id: int, cmd: UpdateDataSourceCommand, current_user: User
) -> DataSourceResponse:
    ds = crud_datasource.get(db=db, ds_id=ds_id)
    if not ds:
        raise LabelUException(
            code=ErrorCode.CODE_61000_NO_DATA,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    obj_in = cmd.model_dump(exclude_unset=True)
    if "access_key_id" in obj_in and obj_in["access_key_id"] is not None:
        obj_in["access_key_id"] = encrypt_value(obj_in["access_key_id"])
    if "secret_access_key" in obj_in and obj_in["secret_access_key"] is not None:
        obj_in["secret_access_key"] = encrypt_value(obj_in["secret_access_key"])
    obj_in["updated_by"] = current_user.id
    with begin_transaction(db):
        ds = crud_datasource.update(db=db, db_obj=ds, obj_in=obj_in)
    return _to_response(ds)


async def delete(db: Session, ds_id: int, current_user: User) -> None:
    ds = crud_datasource.get(db=db, ds_id=ds_id)
    if not ds:
        raise LabelUException(
            code=ErrorCode.CODE_61000_NO_DATA,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    with begin_transaction(db):
        crud_datasource.soft_delete(db=db, db_obj=ds)


# ── S3 file listing ──────────────────────────────────────────────────

async def list_objects(
    db: Session,
    ds_id: int,
    prefix: Optional[str] = None,
    extension: Optional[str] = None,
    page_token: Optional[str] = None,
    size: int = 100,
) -> S3ObjectListResponse:
    ds = crud_datasource.get(db=db, ds_id=ds_id)
    if not ds:
        raise LabelUException(
            code=ErrorCode.CODE_61000_NO_DATA,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    client = _build_s3_client(ds)
    full_prefix = prefix if prefix is not None else (ds.prefix or "")

    kwargs = {
        "Bucket": ds.bucket,
        "Prefix": full_prefix,
        "MaxKeys": size,
    }
    if page_token:
        kwargs["ContinuationToken"] = page_token

    allowed_exts = None
    if extension:
        allowed_exts = {("." + e.strip().lower().lstrip(".")) for e in extension.split(",") if e.strip()}

    try:
        resp = client.list_objects_v2(**kwargs)
    except Exception as exc:
        logger.opt(exception=exc).error("S3 list_objects_v2 failed for datasource {}", ds_id)
        raise LabelUException(
            code=ErrorCode.CODE_62002_S3_REQUEST_FAILED,
            status_code=status.HTTP_502_BAD_GATEWAY,
        )

    objects: list[S3ObjectItem] = []
    for obj in resp.get("Contents", []):
        key: str = obj["Key"]
        if key.endswith("/"):
            continue
        if allowed_exts:
            ext = "." + key.rsplit(".", 1)[-1].lower() if "." in key else ""
            if ext not in allowed_exts:
                continue
        objects.append(S3ObjectItem(
            key=key,
            size=obj.get("Size", 0),
            last_modified=obj.get("LastModified", "").isoformat() if obj.get("LastModified") else None,
        ))

    return S3ObjectListResponse(
        objects=objects,
        next_page_token=resp.get("NextContinuationToken"),
        truncated=resp.get("IsTruncated", False),
    )
