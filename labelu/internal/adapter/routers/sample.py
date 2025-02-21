from typing import List, Union

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, status, Security
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.common import db
from labelu.internal.common.security import security
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.domain.models.user import User
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import sample as service
from labelu.internal.application.command.sample import ExportType
from labelu.internal.application.command.sample import PatchSampleCommand
from labelu.internal.application.command.sample import CreateSampleCommand
from labelu.internal.application.command.sample import DeleteSampleCommand
from labelu.internal.application.command.sample import ExportSampleCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.base import MetaData
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.base import OkRespWithMeta
from labelu.internal.application.response.sample import SampleResponse
from labelu.internal.application.response.sample import CreateSampleResponse


router = APIRouter(prefix="/tasks", tags=["samples"])


@router.post(
    "/{task_id}/samples",
    response_model=OkResp[CreateSampleResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    task_id: int,
    cmd: List[CreateSampleCommand],
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a sample.
    """

    # business logic
    data = await service.create(
        db=db, task_id=task_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[CreateSampleResponse](data=data)


@router.get(
    "/{task_id}/samples",
    response_model=OkRespWithMeta[List[SampleResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_by(
    task_id: int,
    after: Union[int, None] = Query(default=None, gt=0),
    before: Union[int, None] = Query(default=None, gt=0),
    page: Union[int, None] = Query(default=None, ge=0),
    size: Union[int, None] = 100,
    sort: Union[str, None] = Query(
        default=None, regex="(annotated_count|state|inner_id|updated_at):(desc|asc)"
    ),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a annotation result.
    """

    if len([i for i in (after, before, page) if i != None]) != 1:
        raise LabelUException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=ErrorCode.CODE_55000_SAMPLE_LIST_PARAMETERS_ERROR,
        )

    # business logic
    data, total = await service.list_by(
        db=db,
        task_id=task_id,
        after=after,
        before=before,
        page=page,
        size=size,
        sorting=sort,
    )

    # response
    meta_data = MetaData(total=total, page=page, size=len(data))
    return OkRespWithMeta[List[SampleResponse]](meta_data=meta_data, data=data)


@router.get(
    "/{task_id}/samples/{sample_id}",
    response_model=OkResp[SampleResponse],
    status_code=status.HTTP_200_OK,
)
async def get(
    task_id: int,
    sample_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a annotation result.
    """

    # business logic
    data = await service.get(
        db=db, task_id=task_id, sample_id=sample_id
    )

    # response
    return OkResp[SampleResponse](data=data)


@router.patch(
    "/{task_id}/samples/{sample_id}",
    response_model=OkResp[SampleResponse],
    status_code=status.HTTP_200_OK,
)
async def update(
    task_id: int,
    sample_id: int,
    cmd: PatchSampleCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    update a annotation.
    """

    # business logic
    data = await service.patch(
        db=db, task_id=task_id, sample_id=sample_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[SampleResponse](data=data)


@router.delete(
    "/{task_id}/samples",
    response_model=OkResp[CommonDataResp],
    status_code=status.HTTP_200_OK,
)
async def delete(
    cmd: DeleteSampleCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    delete a annotation.
    """

    # business logic
    data = await service.delete(
        db=db, sample_ids=cmd.sample_ids, current_user=current_user
    )

    # response
    return OkResp[CommonDataResp](data=data)


@router.post(
    "/{task_id}/samples/export",
    status_code=status.HTTP_200_OK,
)
async def export(
    task_id: int,
    export_type: ExportType,
    cmd: ExportSampleCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    export data.
    """

    # business logic
    data = await service.export(
        db=db,
        task_id=task_id,
        export_type=export_type,
        sample_ids=cmd.sample_ids,
        current_user=current_user,
    )

    # response
    media_type = ".json" if data.suffix == ".json" else data.suffix.strip(".")
    return FileResponse(
        path=data, filename=data.name, media_type=f"application/{media_type}"
    )
