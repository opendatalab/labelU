from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, Form, status, Depends, Security
from fastapi import File, Header, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.common import db
from labelu.internal.common.config import settings
from labelu.internal.common.security import security
from labelu.internal.domain.models.user import User
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import task as service
from labelu.internal.application.command.task import UploadCommand
from labelu.internal.application.command.task import BasicConfigCommand
from labelu.internal.application.command.task import UpdateCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.base import MetaData
from labelu.internal.application.response.base import OkRespWithMeta
from labelu.internal.application.response.task import TaskResponse
from labelu.internal.application.response.task import UploadResponse
from labelu.internal.application.response.task import TaskFileResponse
from labelu.internal.application.response.task import TaskResponseWithProgress


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "",
    response_model=OkResp[TaskResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    cmd: BasicConfigCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a task with basic config.
    """

    # business logic
    data = await service.create(db=db, cmd=cmd, current_user=current_user)

    # response
    return OkResp[TaskResponse](data=data)


@router.get(
    "",
    response_model=OkRespWithMeta[List[TaskResponseWithProgress]],
    status_code=status.HTTP_200_OK,
)
async def list(
    page: int = 0,
    size: int = 100,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a task with basic config.
    """

    # business logic
    data, total = await service.list(
        db=db, current_user=current_user, page=page, size=size
    )

    # response
    meta_data = MetaData(total=total, page=page, size=len(data))
    return OkRespWithMeta[List[TaskResponseWithProgress]](
        meta_data=meta_data, data=data
    )


@router.get(
    "/{task_id}",
    response_model=OkResp[TaskResponseWithProgress],
    status_code=status.HTTP_200_OK,
)
async def get(
    task_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    get task detail.
    """

    # business logic
    data = await service.get(db=db, task_id=task_id, current_user=current_user)

    # response
    return OkResp[TaskResponseWithProgress](data=data)


@router.post(
    "/{task_id}/upload",
    response_model=OkResp[UploadResponse],
    status_code=status.HTTP_201_CREATED,
)
async def upload(
    task_id: int,
    file: UploadFile = File(...),
    path: str = Form(default=""),
    content_length: int = Header(..., lt=settings.UPLOAD_FILE_MAX_SIZE),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload file annnotate data.
    """
    # business logic
    cmd = UploadCommand(file=file, path=path)
    data = await service.upload(
        db=db, task_id=task_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[UploadResponse](data=data)


@router.put(
    "/{task_id}",
    response_model=OkResp[TaskResponse],
    status_code=status.HTTP_200_OK,
)
async def update(
    task_id: int,
    cmd: UpdateCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    update task info, inlucde annotation config, name, description and tips.
    """

    # business logic
    data = await service.update(db=db, task_id=task_id, cmd=cmd)

    # response
    return OkResp[TaskResponse](data=data)


@router.get(
    "/{task_id}/uploads",
    response_model=OkRespWithMeta[List[TaskFileResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_upload_files(
    task_id: int,
    page: int = 0,
    size: int = 100,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    get task upload file detail.
    """

    # business logic
    data, total = await service.list_upload_files(
        db=db, task_id=task_id, current_user=current_user, page=page, size=size
    )

    # response
    meta_data = MetaData(total=total, page=page, size=len(data))
    return OkRespWithMeta[List[TaskFileResponse]](meta_data=meta_data, data=data)


@router.get(
    "/{task_id}/uploads/{file_id}",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
)
async def get_upload_file(
    task_id: int,
    file_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    get task upload file detail.
    """

    # business logic
    data = await service.get_upload_file(
        db=db, task_id=task_id, file_id=file_id, current_user=current_user
    )

    # response
    return data
