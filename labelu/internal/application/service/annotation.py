from typing import List

from sqlalchemy.orm import Session

from labelu.internal.domain.models.user import User
from labelu.internal.application.command.annotation import SubmitResultCommand
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.annotation import TaskAnnotationResponse


async def create(
    db: Session, task_file_id: int, cmd: SubmitResultCommand, current_user: User
) -> TaskAnnotationResponse:

    # response
    return TaskAnnotationResponse()


async def get(
    db: Session, task_file_id: int, current_user: User
) -> List[TaskAnnotationResponse]:

    # response
    return []


async def update(
    db: Session, annotation_id: int, cmd: SubmitResultCommand, current_user: User
) -> TaskAnnotationResponse:

    # response
    return TaskAnnotationResponse()


async def delete(db: Session, annotation_id: int, current_user: User) -> CommonDataResp:

    # response
    return CommonDataResp(ok=True)
