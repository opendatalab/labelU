import aiofiles
import uuid
from typing import List, Tuple
from pathlib import Path

from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.common.config import settings
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import UnicornException
from labelu.internal.domain.models.user import User
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task import TaskFile
from labelu.internal.domain.models.task import TaskStatus
from labelu.internal.adapter.persistence import crud_user
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.application.command.task import UploadCommand
from labelu.internal.application.command.task import BasicConfigCommand
from labelu.internal.application.command.task import UpdateCommand
from labelu.internal.application.response.task import TaskResponse
from labelu.internal.application.response.task import UploadResponse
from labelu.internal.application.response.task import TaskFileResponse
from labelu.internal.application.response.task import User as UserResponse
from labelu.internal.application.response.task import TaskResponseWithProgress


async def create(
    db: Session, cmd: BasicConfigCommand, current_user: User
) -> TaskResponse:
    # new a task
    new_task = crud_task.create(
        db=db,
        task=Task(
            status=TaskStatus.DRAFT.value,
            name=cmd.name,
            description=cmd.description,
            tips=cmd.tips,
            created_by=current_user.id,
            updated_by=current_user.id,
        ),
    )

    # response
    return TaskResponse(
        id=new_task.id,
        name=new_task.name,
        description=new_task.description,
        tips=new_task.tips,
        status=new_task.status,
        created_at=new_task.created_at,
    )


async def list(
    db: Session,
    current_user: User,
    page: int,
    size: int,
) -> Tuple[List[TaskResponseWithProgress], int]:

    # get task total count
    total_task = crud_task.count(db=db, owner_id=current_user.id)

    # get task list
    tasks = crud_task.list(db=db, owner_id=current_user.id, page=page, size=size)

    # get progress
    total_task_file = crud_task.count_task_file_group_by_task(
        db=db,
        owner_id=current_user.id,
    )
    count_task_file_in_progress = crud_task.count_task_file_group_by_task(
        db=db, owner_id=current_user.id, annotated_status=[TaskStatus.INPROGRESS.value]
    )

    # response
    list = [
        TaskResponseWithProgress(
            id=t.id,
            name=t.name,
            description=t.description,
            tips=t.tips,
            media_type=t.media_type,
            config=t.config,
            status=t.status,
            created_at=t.created_at,
            annotated_count=count_task_file_in_progress.get(t.id, 0),
            total=total_task_file.get(t.id, 0),
        )
        for t in tasks
    ]
    return list, total_task


async def get(
    db: Session, task_id: int, current_user: User
) -> TaskResponseWithProgress:

    # get task detail
    task = crud_task.get(db=db, id=task_id)

    # get progress
    total_task_file = crud_task.count_task_file_group_by_task(
        db=db,
        owner_id=current_user.id,
        task_id=task.id,
    )
    count_task_file_in_progress = crud_task.count_task_file_group_by_task(
        db=db,
        owner_id=current_user.id,
        task_id=task.id,
        annotated_status=[TaskStatus.INPROGRESS.value],
    )

    # response
    return TaskResponseWithProgress(
        id=task.id,
        name=task.name,
        description=task.description,
        tips=task.tips,
        media_type=task.media_type,
        config=task.config,
        status=task.status,
        created_at=task.created_at,
        annotated_count=count_task_file_in_progress.get(task.id, 0),
        total=total_task_file.get(task.id, 0),
    )


async def upload(
    db: Session, task_id: int, cmd: UploadCommand, current_user: User
) -> UploadResponse:

    # save file
    try:
        # file relative path
        file_relative_base_dir = Path(settings.UPLOAD_DIR).joinpath(
            str(task_id), cmd.path.strip()
        )
        file_relative_path = str(
            file_relative_base_dir.joinpath(
                str(uuid.uuid4())[0:8] + "-" + cmd.file.filename
            )
        )

        # file full path
        file_full_base_dir = Path(settings.MEDIA_ROOT).joinpath(file_relative_base_dir)
        file_full_path = Path(settings.MEDIA_ROOT).joinpath(file_relative_path)

        # create dicreatory
        file_full_base_dir.mkdir(parents=True, exist_ok=True)
        async with aiofiles.open(file_full_path, "wb") as out_file:
            content = await cmd.file.read()  # async read
            await out_file.write(content)  # async write
    except:
        raise UnicornException(
            code=ErrorCode.CODE_51000_TASK_FILE_UPLOAD_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # check file already saved
    task_file_status = False
    if file_full_path.exists():
        task_file_status = True
    # add a task file record
    task_file_id = 0
    try:
        task_file = crud_task.add_file(
            db=db,
            task_file=TaskFile(
                path=file_relative_path,
                created_by=current_user.id,
                updated_by=current_user.id,
                task_id=task_id,
                status=task_file_status,
            ),
        )
        task_file_id = task_file.id
    except Exception as e:
        task_file_status = False
        logger.error(e)
    # response
    return UploadResponse(
        id=task_file_id, filename=file_relative_path, status=task_file_status
    )


async def update(db: Session, task_id: int, cmd: UpdateCommand) -> TaskResponse:

    # get old task
    task = crud_task.get(db=db, id=task_id)

    # update
    obj_in = cmd.dict(exclude_unset=True)
    if cmd.config and cmd.media_type:
        obj_in[Task.status.key] = TaskStatus.CONFIGURED
    else:
        obj_in[Task.media_type.key] = None
        obj_in[Task.config.key] = None
    updated_task = crud_task.update(db=db, db_obj=task, obj_in=obj_in)

    # response
    return TaskResponse(
        id=updated_task.id,
        name=updated_task.name,
        description=updated_task.description,
        tips=updated_task.tips,
        media_type=updated_task.media_type,
        config=updated_task.config,
        status=updated_task.status,
        created_at=updated_task.created_at,
    )


async def list_upload_files(
    db: Session,
    task_id: int,
    current_user: User,
    page: int,
    size: int,
) -> Tuple[List[TaskFileResponse], int]:

    # get task file total count
    total_task_file = crud_task.count_task_file(
        db=db, task_id=task_id, owner_id=current_user.id
    )

    # get task file list
    task_files = crud_task.list_upload_files(
        db=db, task_id=task_id, owner_id=current_user.id, page=page, size=size
    )

    # all annotated user
    user_ids = [f.updated_by for f in task_files]
    users = crud_user.list(db=db, user_ids=user_ids)
    user_id_map = {}
    for u in users:
        user_id_map[u.id] = u

    # response
    list = []
    for f in task_files:
        user = user_id_map.get(f.updated_by)
        if user:
            annotated_by = UserResponse(id=user.id, username=user.username)
        else:
            annotated_by = None
        list.append(
            TaskFileResponse(
                id=f.id,
                path=f.path,
                task_id=f.task_id,
                annotated=f.annotated,
                result=f.result,
                annotated_by=annotated_by,
                annotated_at=f.updated_at,
            )
        )
    return list, total_task_file


async def get_upload_file(
    db: Session, task_id: int, file_id: int, current_user: User
) -> str:

    # get file path
    task_file = crud_task.get_file(db=db, id=file_id)

    # response
    return Path(settings.MEDIA_ROOT, f"{task_file.path}")
