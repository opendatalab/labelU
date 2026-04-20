from typing import List, Union

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, status, Security
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.common import db as db_module
from labelu.internal.common.security import security
from labelu.internal.domain.models.user import User
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import datasource as service
from labelu.internal.application.command.datasource import (
    CreateDataSourceCommand,
    UpdateDataSourceCommand,
)
from labelu.internal.application.response.base import (
    CommonDataResp,
    MetaData,
    OkResp,
    OkRespWithMeta,
)
from labelu.internal.application.response.datasource import (
    DataSourceResponse,
    S3ObjectListResponse,
)

router = APIRouter(prefix="/datasources", tags=["datasources"])


@router.post(
    "",
    response_model=OkResp[DataSourceResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    cmd: CreateDataSourceCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    data = await service.create(db=db, cmd=cmd, current_user=current_user)
    return OkResp[DataSourceResponse](data=data)


@router.get(
    "",
    response_model=OkRespWithMeta[List[DataSourceResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_all(
    page: int = Query(default=0, ge=0),
    size: int = Query(default=100, ge=1, le=500),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    data, total = await service.list_by(db=db, current_user=current_user, page=page, size=size)
    return OkRespWithMeta[List[DataSourceResponse]](
        meta_data=MetaData(total=total, page=page, size=len(data)),
        data=data,
    )


@router.get(
    "/{ds_id}",
    response_model=OkResp[DataSourceResponse],
    status_code=status.HTTP_200_OK,
)
async def get(
    ds_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    data = await service.get(db=db, ds_id=ds_id)
    return OkResp[DataSourceResponse](data=data)


@router.patch(
    "/{ds_id}",
    response_model=OkResp[DataSourceResponse],
    status_code=status.HTTP_200_OK,
)
async def update(
    ds_id: int,
    cmd: UpdateDataSourceCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    data = await service.update(db=db, ds_id=ds_id, cmd=cmd, current_user=current_user)
    return OkResp[DataSourceResponse](data=data)


@router.delete(
    "/{ds_id}",
    response_model=OkResp[CommonDataResp],
    status_code=status.HTTP_200_OK,
)
async def delete(
    ds_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    await service.delete(db=db, ds_id=ds_id, current_user=current_user)
    return OkResp[CommonDataResp](data=CommonDataResp(ok=True))


@router.get(
    "/{ds_id}/objects",
    response_model=OkResp[S3ObjectListResponse],
    status_code=status.HTTP_200_OK,
)
async def list_objects(
    ds_id: int,
    prefix: Union[str, None] = Query(default=None),
    extension: Union[str, None] = Query(default=None, description="Comma-separated extensions, e.g. .jpg,.png"),
    page_token: Union[str, None] = Query(default=None),
    size: int = Query(default=100, ge=1, le=1000),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    data = await service.list_objects(
        db=db, ds_id=ds_id, prefix=prefix, extension=extension,
        page_token=page_token, size=size,
    )
    return OkResp[S3ObjectListResponse](data=data)
