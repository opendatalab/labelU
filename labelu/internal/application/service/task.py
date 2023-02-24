import shutil
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
from labelu.internal.domain.models.task import TaskStatus
from labelu.internal.domain.models.sample import SampleState
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.application.command.task import BasicConfigCommand
from labelu.internal.application.command.task import UpdateCommand
from labelu.internal.application.response.base import UserResp
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.task import TaskStatics
from labelu.internal.application.response.task import TaskResponse
from labelu.internal.application.response.task import TaskResponseWithStatics


async def create(
    db: Session, cmd: BasicConfigCommand, current_user: User
) -> TaskResponse:
    # new a task

    with db.begin():
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
        created_by=UserResp(
            id=new_task.owner.id,
            username=new_task.owner.username,
        ),
    )


async def list_by(
    db: Session,
    current_user: User,
    page: int,
    size: int,
) -> Tuple[List[TaskResponseWithStatics], int]:

    # get task total count
    total_task = crud_task.count(db=db, owner_id=current_user.id)

    # get task list
    tasks = crud_task.list_by(db=db, owner_id=current_user.id, page=page, size=size)

    # get progress
    task_ids = [task.id for task in tasks]
    statics = crud_sample.statics(db=db, owner_id=current_user.id, task_ids=task_ids)

    # response
    tasks_with_statics = [
        TaskResponseWithStatics(
            id=task.id,
            name=task.name,
            description=task.description,
            tips=task.tips,
            media_type=task.media_type,
            config=task.config,
            status=task.status,
            created_at=task.created_at,
            created_by=UserResp(
                id=task.owner.id,
                username=task.owner.username,
            ),
            stats=TaskStatics(
                new=statics.get(f"{task.id}_{SampleState.NEW.value}", 0),
                done=statics.get(f"{task.id}_{SampleState.DONE.value}", 0),
                skipped=statics.get(f"{task.id}_{SampleState.SKIPPED.value}", 0),
            ),
        )
        for task in tasks
    ]
    return tasks_with_statics, total_task


async def get(db: Session, task_id: int, current_user: User) -> TaskResponseWithStatics:

    # get task detail
    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        logger.error("cannot find task:{}", task_id)
        raise UnicornException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # get progress
    statics = crud_sample.statics(
        db=db,
        owner_id=current_user.id,
        task_ids=[task.id],
    )

    # response
    return TaskResponseWithStatics(
        id=task.id,
        name=task.name,
        description=task.description,
        tips=task.tips,
        media_type=task.media_type,
        config=task.config,
        status=task.status,
        created_at=task.created_at,
        created_by=UserResp(
            id=task.owner.id,
            username=task.owner.username,
        ),
        stats=TaskStatics(
            new=statics.get(f"{task.id}_{SampleState.NEW.value}", 0),
            done=statics.get(f"{task.id}_{SampleState.DONE.value}", 0),
            skipped=statics.get(f"{task.id}_{SampleState.SKIPPED.value}", 0),
        ),
    )


async def update(db: Session, task_id: int, cmd: UpdateCommand) -> TaskResponse:

    # get task
    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        logger.error("cannot find task:{}", task_id)
        raise UnicornException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # update
    obj_in = cmd.dict(exclude_unset=True)
    if cmd.config and cmd.media_type:
        obj_in[Task.status.key] = TaskStatus.CONFIGURED
    else:
        obj_in[Task.media_type.key] = None
        obj_in[Task.config.key] = None
    with db.begin():
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
        created_by=UserResp(
            id=updated_task.owner.id,
            username=updated_task.owner.username,
        ),
    )


async def delete(db: Session, task_id: int, current_user: User) -> CommonDataResp:

    # get task
    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        logger.error("cannot find task:{}", task_id)
        raise UnicornException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if task.created_by != current_user.id:
        logger.error(
            "cannot delete task, the task owner is:{}, the delete operator is:{}",
            task.created_by,
            current_user.id,
        )
        raise UnicornException(
            code=ErrorCode.CODE_30001_NO_PERMISSION,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # delete
    with db.begin():
        crud_task.delete(db=db, db_obj=task)

    # delete media
    try:
        file_relative_base_dir = Path(settings.UPLOAD_DIR).joinpath(str(task_id))
        file_full_base_dir = Path(settings.MEDIA_ROOT).joinpath(file_relative_base_dir)
        shutil.rmtree(file_full_base_dir)
    except Exception as e:
        logger.error(e)

    # response
    return CommonDataResp(ok=True)
