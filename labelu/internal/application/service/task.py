import os
import aiofiles
from typing import List, Tuple
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
            status=TaskStatus.DRAFT.value,
            name=cmd.name,
            description=cmd.description,
            tips=cmd.tips,
            updated_by=current_user.id,
        ),
    )

    # response
    return TaskResponse(
        id=task.id, name=task.name, description=task.description, tips=task.tips
    )


async def list(
    db: Session,
    current_user: User,
    page: int,
    size: int,
) -> Tuple[List[TaskResponse], int]:

    # get task total count
    total_task = crud_task.count(db=db, owner_id=current_user.id)

    # get task list
    tasks = crud_task.list(db=db, owner_id=current_user.id, page=page, size=size)

    # get progress
    total_task_file = crud_task.count_group_by_task(
        db=db,
        owner_id=current_user.id,
    )
    count_task_file_in_progress = crud_task.count_group_by_task(
        db=db, owner_id=current_user.id, annotated_status=[TaskStatus.INPROGRESS.value]
    )

    # response
    list = [
        TaskResponse(
            id=t.id,
            name=t.name,
            description=t.description,
            tips=t.tips,
            config=t.config,
            media_type=t.media_type,
            annotated_count=count_task_file_in_progress.get(t.id, 0),
            total=total_task_file.get(t.id, 0),
        )
        for t in tasks
    ]
    return list, total_task


async def upload(
    db: Session, task_id: int, cmd: UploadCommand, current_user: User
) -> UploadResponse:

    # save file
    path = os.path.join(settings.BASE_DATA_DIR, f"{task_id}", f"{cmd.path}")
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
