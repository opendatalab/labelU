import json
import uuid
from datetime import datetime
from typing import List, Tuple, Union

from pathlib import Path
from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.common.config import settings
from labelu.internal.common.converter import converter
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import UnicornException
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.domain.models.user import User
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task import TaskStatus
from labelu.internal.domain.models.sample import TaskSample
from labelu.internal.domain.models.sample import SampleState
from labelu.internal.application.command.sample import ExportType
from labelu.internal.application.command.sample import PatchSampleCommand
from labelu.internal.application.command.sample import CreateSampleCommand
from labelu.internal.application.response.base import UserResp
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.sample import CreateSampleResponse
from labelu.internal.application.response.sample import SampleResponse


async def create(
    db: Session, task_id: int, cmd: List[CreateSampleCommand], current_user: User
) -> CreateSampleResponse:

    # check task exist
    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        logger.error("cannot find task:{}", task_id)
        raise UnicornException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    samples = [
        TaskSample(
            task_id=task_id,
            task_attachment_ids=str(sample.attachement_ids),
            created_by=current_user.id,
            updated_by=current_user.id,
            data=json.dumps(sample.data),
        )
        for sample in cmd
    ]

    with db.begin():
        if task.status == TaskStatus.DRAFT.value:
            obj_in = {Task.status.key: TaskStatus.IMPORTED}
            crud_task.update(db=db, db_obj=task, obj_in=obj_in)
        new_samples = crud_sample.batch(db=db, samples=samples)

    # response
    ids = [s.id for s in new_samples]
    return CreateSampleResponse(ids=ids)


async def list_by(
    db: Session,
    task_id: Union[int, None],
    after: Union[int, None],
    before: Union[int, None],
    pageNo: Union[int, None],
    pageSize: int,
    sorting: Union[str, None],
    current_user: User,
) -> Tuple[List[SampleResponse], int]:

    samples = crud_sample.list_by(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
        after=after,
        before=before,
        pageNo=pageNo,
        pageSize=pageSize,
        sorting=sorting,
    )

    total = crud_sample.count(db=db, task_id=task_id, owner_id=current_user.id)

    # response
    return [
        SampleResponse(
            id=sample.id,
            state=sample.state,
            data=json.loads(sample.data),
            annotated_count=sample.annotated_count,
            created_at=sample.created_at,
            created_by=UserResp(
                id=sample.owner.id,
                username=sample.owner.username,
            ),
            updated_at=sample.updated_at,
            updated_by=UserResp(
                id=sample.updater.id,
                username=sample.updater.username,
            ),
        )
        for sample in samples
    ], total


async def get(db: Session, sample_id: int, current_user: User) -> SampleResponse:
    sample = crud_sample.get(
        db=db,
        sample_id=sample_id,
    )

    if not sample:
        logger.error("cannot find sample:{}", sample_id)
        raise UnicornException(
            code=ErrorCode.CODE_55001_SAMPLE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # response
    return SampleResponse(
        id=sample.id,
        state=sample.state,
        data=json.loads(sample.data),
        annotated_count=sample.annotated_count,
        created_at=sample.created_at,
        created_by=UserResp(
            id=sample.owner.id,
            username=sample.owner.username,
        ),
        updated_at=sample.updated_at,
        updated_by=UserResp(
            id=sample.updater.id,
            username=sample.updater.username,
        ),
    )


async def patch(
    db: Session, task_id:int, sample_id: int, cmd: PatchSampleCommand, current_user: User
) -> SampleResponse:

    # check task exist
    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        logger.error("cannot find task:{}", task_id)
        raise UnicornException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # get sample
    sample = crud_sample.get(db=db, sample_id=sample_id)
    if not sample:
        logger.error("cannot find sample:{}", sample_id)
        raise UnicornException(
            code=ErrorCode.CODE_55001_SAMPLE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # update
    sample_obj_in = {}
    if cmd.state == SampleState.SKIPPED.value:
        sample_obj_in[TaskSample.state.key] = SampleState.SKIPPED.value
    elif cmd.state == SampleState.NEW.value:
        sample_obj_in[TaskSample.data.key] = json.dumps(cmd.data)
        sample_obj_in[TaskSample.annotated_count.key] = cmd.annotated_count
        sample_obj_in[TaskSample.state.key] = SampleState.NEW.value
    else:  # can be None, or DONE
        sample_obj_in[TaskSample.data.key] = json.dumps(cmd.data)
        sample_obj_in[TaskSample.annotated_count.key] = cmd.annotated_count
        sample_obj_in[TaskSample.state.key] = SampleState.DONE.value

    with db.begin():
        # update task status
        if task.status != TaskStatus.FINISHED.value:
            statics = crud_sample.statics(db=db, owner_id=current_user.id, task_ids=[task_id])
            task_obj_in = {Task.status.key:TaskStatus.INPROGRESS.value}
            if statics.get(f"{task.id}_{SampleState.NEW.value}", 0) <= 1:
                task_obj_in[Task.status.key] = TaskStatus.FINISHED.value
            if task.status != task_obj_in[Task.status.key]:
                crud_task.update(db=db, db_obj=task, obj_in=task_obj_in)
        # update task sample result
        updated_sample = crud_sample.update(db=db, db_obj=sample, obj_in=sample_obj_in)

    # response
    return SampleResponse(
        id=updated_sample.id,
        state=updated_sample.state,
        data=json.loads(updated_sample.data),
        annotated_count=updated_sample.annotated_count,
        created_at=updated_sample.created_at,
        created_by=UserResp(
            id=updated_sample.owner.id,
            username=updated_sample.owner.username,
        ),
        updated_at=updated_sample.updated_at,
        updated_by=UserResp(
            id=updated_sample.updater.id,
            username=updated_sample.updater.username,
        ),
    )


async def delete(
    db: Session, sample_ids: List[int], current_user: User
) -> CommonDataResp:

    with db.begin():
        crud_sample.delete(db=db, sample_ids=sample_ids)
    # response
    return CommonDataResp(ok=True)


async def export(
    db: Session,
    task_id: int,
    export_type: ExportType,
    sample_ids: List[int],
    current_user: User,
) -> str:

    task = crud_task.get(db=db, task_id=task_id)
    samples = crud_sample.get_by_ids(db=db, sample_ids=sample_ids)
    data = [sample.__dict__ for sample in samples if sample.state == SampleState.DONE]

    # output data path
    out_data_dir = Path(settings.MEDIA_ROOT).joinpath(
        settings.EXOIRT_DIR,
        f"task-{task_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[0:8]}",
    )

    # converter to export_type
    try:
        file_full_path = converter.convert(
            config=json.loads(task.config),
            input_data=data,
            out_data_dir=out_data_dir,
            out_data_file_name_prefix=task_id,
            format=export_type.value,
        )
    except Exception as e:
        logger.error(data)
        logger.error(e)
        raise UnicornException(
            code=ErrorCode.CODE_55002_SAMPLE_FORMAT_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # response
    return file_full_path
