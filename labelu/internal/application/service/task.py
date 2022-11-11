from sqlalchemy.orm import Session

from labelu.internal.domain.models.user import User
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task import TaskStatus
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.application.command.task import UploadCommand
from labelu.internal.application.command.task import BasicConfigCommand
from labelu.internal.application.command.task import UpdateCommand
from labelu.internal.application.response.task import TaskResponse
from labelu.internal.application.response.task import UploadResponse


async def create(
    db: Session, cmd: BasicConfigCommand, current_user: User
) -> TaskResponse:
    # new a task
    task = crud_task.create(
        db=db,
        task=Task(
            user_id=current_user.id,
            status=TaskStatus.DRAFT,
            name=cmd.name,
            description=cmd.description,
            tips=cmd.tips,
        ),
    )

    # response
    return TaskResponse(
        id=task.id, name=task.name, description=task.description, tips=task.tips
    )


async def uploads(db: Session, cmd: UploadCommand) -> UploadResponse:
    # response
    return TaskResponse()


async def update(db: Session, cmd: UpdateCommand) -> TaskResponse:
    # response
    return TaskResponse()
