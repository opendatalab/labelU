from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Security
from fastapi import UploadFile, File
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.common import db
from labelu.internal.domain.models.user import User
from labelu.internal.common.security import security
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import task as service
from labelu.internal.application.command.task import UploadCommand
from labelu.internal.application.command.task import BasicConfigCommand
from labelu.internal.application.command.task import UpdateCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.task import TaskResponse
from labelu.internal.application.response.task import UploadResponse


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


@router.post(
    "/{task_id}/upload",
    response_model=OkResp[TaskResponse],
    status_code=status.HTTP_201_CREATED,
)
async def uploads(
    task_id: int,
    file: UploadFile = File(...),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Upload files as annnotate data.
    """

    # business logic
    cmd = UploadCommand(file=file)
    data = await service.uploads(db=db, cmd=cmd)

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
    data = await service.update(db=db, cmd=cmd)

    # response
    return OkResp[TaskResponse](data=data)
