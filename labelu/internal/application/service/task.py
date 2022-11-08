from sqlalchemy.orm import Session

from labelu.internal.common import db
from labelu.internal.application.command.task import UploadCommand
from labelu.internal.application.command.task import BasicConfigCommand
from labelu.internal.application.command.task import UpdateCommand
from labelu.internal.application.response.task import TaskResponse
from labelu.internal.application.response.task import UploadResponse


async def create(db: Session, cmd: BasicConfigCommand) -> TaskResponse:
    # response
    return TaskResponse()


async def uploads(db: Session, cmd: UploadCommand) -> UploadResponse:
    # response
    return TaskResponse()


async def update(db: Session, cmd: UpdateCommand) -> TaskResponse:
    # response
    return TaskResponse()
