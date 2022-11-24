from typing import List

from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Security
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.common import db
from labelu.internal.common.security import security
from labelu.internal.domain.models.user import User
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import annotation as service
from labelu.internal.application.command.annotation import SubmitResultCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.annotation import TaskAnnotationResponse


router = APIRouter(prefix="/annotations", tags=["annotations"])


@router.post(
    "",
    response_model=OkResp[TaskAnnotationResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    task_file_id: int,
    cmd: SubmitResultCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a annotation.
    """

    # business logic
    data = await service.create(
        db=db, task_file_id=task_file_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[TaskAnnotationResponse](data=data)


@router.get(
    "",
    response_model=OkResp[List[TaskAnnotationResponse]],
    status_code=status.HTTP_200_OK,
)
async def get(
    task_file_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a annotation result.
    """

    # business logic
    data = await service.get(
        db=db, task_file_id=task_file_id, current_user=current_user
    )

    # response
    return OkResp[List[TaskAnnotationResponse]](data=data)


@router.put(
    "/{annotation_id}",
    response_model=OkResp[TaskAnnotationResponse],
    status_code=status.HTTP_200_OK,
)
async def update(
    annotation_id: int,
    cmd: SubmitResultCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    update a annotation.
    """

    # business logic
    data = await service.update(
        db=db, annotation_id=annotation_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[TaskAnnotationResponse](data=data)


@router.delete(
    "/{annotation_id}",
    response_model=OkResp[TaskAnnotationResponse],
    status_code=status.HTTP_200_OK,
)
async def delete(
    annotation_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    delete a annotation.
    """

    # business logic
    data = await service.delete(
        db=db, annotation_id=annotation_id, current_user=current_user
    )

    # response
    return OkResp[CommonDataResp](data=data)
