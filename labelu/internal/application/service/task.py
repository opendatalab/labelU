import os
import aiofiles
from sqlalchemy.orm import Session

from labelu.internal.common.config import settings
from labelu.internal.domain.models.user import User
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task import TaskFile
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


async def upload(
    db: Session, task_id: int, cmd: UploadCommand, current_user: User
) -> UploadResponse:

    # save file
    path = os.path.join(settings.BASE_DATA_DIR, f"{task_id}")
    os.makedirs(path, exist_ok=True)
    filepath = os.path.join(path, cmd.file.filename)
    async with aiofiles.open(filepath, "wb") as out_file:
        content = await cmd.file.read()  # async read
        await out_file.write(content)  # async write

    # check file already saved
    if os.path.exists(filepath):
        # add a task file record
        task_file = crud_task.add_file(
            db=db,
            task_file=TaskFile(
                path=f"{task_id}/{cmd.file.filename}",
                user_id=current_user.id,
                task_id=task_id,
            ),
        )

    # response
    return UploadResponse(filename=cmd.file.filename)


async def update(db: Session, cmd: UpdateCommand) -> TaskResponse:
    # response
    return TaskResponse()
