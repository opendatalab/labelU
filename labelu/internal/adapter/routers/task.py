from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.application.response.user import UserResponse
from labelu.internal.common import db
from labelu.internal.common.security import security
from labelu.internal.domain.models.user import User
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import task as service
from labelu.internal.application.command.task import BasicConfigCommand, CollaboratorBatchCommand, CollaboratorUpdateCommand
from labelu.internal.application.command.task import UpdateCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.base import MetaData
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.base import OkRespWithMeta
from labelu.internal.application.response.task import TaskResponse
from labelu.internal.application.response.task import TaskResponseWithStatics


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
    response_model=OkRespWithMeta[List[TaskResponseWithStatics]],
    status_code=status.HTTP_200_OK,
)
async def list_by(
    page: int = 0,
    size: int = 100,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List task.
    """

    # business logic
    data, total = await service.list_by(
        db=db, current_user=current_user, page=page, size=size
    )

    # response
    meta_data = MetaData(total=total, page=page, size=len(data))
    return OkRespWithMeta[List[TaskResponseWithStatics]](meta_data=meta_data, data=data)


@router.get(
    "/{task_id}",
    response_model=OkResp[TaskResponseWithStatics],
    status_code=status.HTTP_200_OK,
)
async def get(
    task_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get task detail.
    """

    # business logic
    data = await service.get(db=db, task_id=task_id, current_user=current_user)

    # response
    return OkResp[TaskResponseWithStatics](data=data)

@router.get(
    "/{task_id}/collaborators",
    response_model=OkResp[List[UserResponse]],
    status_code=status.HTTP_200_OK,
)
async def get_collaborators(
    task_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get task detail.
    """

    # business logic
    data = await service.get_collaborators(db=db, task_id=task_id, current_user=current_user)

    # response
    return OkResp[List[UserResponse]](data=data)

@router.post(
    "/{task_id}/collaborators",
    response_model=OkResp[UserResponse],
    status_code=status.HTTP_201_CREATED,
)
async def add_collaborator(
    task_id: int,
    cmd: CollaboratorUpdateCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add collaborator to task.
    """

    # business logic
    data = await service.add_collaborator(db=db, task_id=task_id, user_id=cmd.user_id, current_user=current_user)

    # response
    return OkResp[UserResponse](data=data)

@router.post(
    "/{task_id}/collaborators/batch_add",
    response_model=OkResp[List[UserResponse]],
    status_code=status.HTTP_201_CREATED,
)
async def batch_add_collaborator_request(
    task_id: int,
    cmd: CollaboratorBatchCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add collaborators to task.
    """

    # business logic
    data = await service.batch_add_collaborators(db=db, task_id=task_id, user_ids=cmd.user_ids, current_user=current_user)

    # response
    return OkResp[List[UserResponse]](data=data)

@router.post(
    "/{task_id}/collaborators/batch_remove",
    response_model=OkResp[CommonDataResp],
    status_code=status.HTTP_201_CREATED,
)
async def batch_remove_collaborator_request(
    task_id: int,
    cmd: CollaboratorBatchCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Add collaborators to task.
    """

    # business logic
    data = await service.batch_remove_collaborators(db=db, task_id=task_id, user_ids=cmd.user_ids, current_user=current_user)

    # response
    return OkResp[CommonDataResp](data=data)


@router.delete(
    "/{task_id}/collaborators/{user_id}",
    response_model=OkResp[CommonDataResp],
    status_code=status.HTTP_200_OK,
)
async def remove_collaborator(
    task_id: int,
    user_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Remove collaborator from task.
    """

    # business logic
    data = await service.remove_collaborator(db=db, task_id=task_id, user_id=user_id, current_user=current_user)

    # response
    return OkResp[CommonDataResp](data=data)


@router.patch(
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
    Update task info, inlucde annotation config, name, description and tips.
    """

    # business logic
    data = await service.update(db=db, task_id=task_id, cmd=cmd)

    # response
    return OkResp[TaskResponse](data=data)


@router.delete(
    "/{task_id}",
    response_model=OkResp[CommonDataResp],
    status_code=status.HTTP_200_OK,
)
async def delete(
    task_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Delete task.
    """

    # business logic
    data = await service.delete(db=db, task_id=task_id, current_user=current_user)

    # response
    return OkResp[CommonDataResp](data=data)
