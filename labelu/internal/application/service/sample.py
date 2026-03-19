import json
import os
import uuid
import asyncio
from datetime import datetime
from typing import List, Tuple, Union

from pathlib import Path
from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.common.config import settings
from labelu.internal.common.converter import converter
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.adapter.persistence import crud_attachment, crud_pre_annotation, crud_task
from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.adapter.persistence import crud_export_job
from labelu.internal.domain.models.pre_annotation import TaskPreAnnotation
from labelu.internal.domain.models.user import User
from labelu.internal.domain.models.task import Task
from labelu.internal.domain.models.task import TaskStatus
from labelu.internal.domain.models.sample import TaskSample
from labelu.internal.domain.models.sample import SampleState
from labelu.internal.domain.models.export_job import ExportStatus
from labelu.internal.application.command.sample import ExportType
from labelu.internal.application.command.sample import PatchSampleCommand
from labelu.internal.application.command.sample import CreateSampleCommand
from labelu.internal.application.response.base import UserResp
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.sample import CreateSampleResponse
from labelu.internal.application.response.sample import SampleResponse
from labelu.internal.application.response.attachment import AttachmentResponse
from labelu.internal.clients.ws import sampleConnectionManager
from labelu.internal.common.websocket import Message, MessageType
from labelu.internal.adapter.ws.sample import TaskSampleWsPayload

def is_sample_pre_annotated(db: Session, task_id: int, sample_name: str | None = None) -> Tuple[List[TaskPreAnnotation], int]:
    if sample_name is None:
        return False
    
    _, total = crud_pre_annotation.list_by(
        db=db,
        task_id=task_id,
        sample_name=sample_name,
        size=1,
    )
    
    return total > 0

async def create(
    db: Session, task_id: int, cmd: List[CreateSampleCommand], current_user: User
) -> CreateSampleResponse:
    obj_in = {}
    with db.begin():
        # check task exist
        task = crud_task.get(db=db, task_id=task_id, lock=True)
        if not task:
            logger.error("cannot find task:{}", task_id)
            raise LabelUException(
                code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        samples = [
            TaskSample(
                inner_id=task.last_sample_inner_id + i + 1,
                task_id=task_id,
                file_id=sample.file_id,
                created_by=current_user.id,
                updated_by=current_user.id,
                data=json.dumps(sample.data, ensure_ascii=False),
            )
            for i, sample in enumerate(cmd)
        ]
        obj_in[Task.last_sample_inner_id.key] = task.last_sample_inner_id + len(cmd)
        if task.status == TaskStatus.DRAFT.value:
            obj_in[Task.status.key] = TaskStatus.IMPORTED
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
    page: Union[int, None],
    size: int,
    sorting: Union[str, None],
) -> Tuple[List[SampleResponse], int]:
    samples = crud_sample.list_by(
        db=db,
        task_id=task_id,
        after=after,
        before=before,
        page=page,
        size=size,
        sorting=sorting,
    )

    total = crud_sample.count(db=db, task_id=task_id)

    # response
    return [
        SampleResponse(
            id=sample.id,
            inner_id=sample.inner_id,
            state=sample.state,
            data=json.loads(sample.data),
            annotated_count=sample.annotated_count,
            is_pre_annotated=is_sample_pre_annotated(db=db, task_id=task_id, sample_name=sample.file.filename if sample.file else None),
            file=AttachmentResponse(id=sample.file.id, filename=sample.file.filename, url=sample.file.url) if sample.file else None,
            created_at=sample.created_at,
            created_by=UserResp(
                id=sample.owner.id,
                username=sample.owner.username,
            ),
            updated_at=sample.updated_at,
            updaters=[UserResp(
                id=updater.id,
                username=updater.username,
            ) for updater in sample.updaters],
        )
        for sample in samples
    ], total


async def get(
    db: Session, task_id: int, sample_id: int
) -> SampleResponse:
    sample = crud_sample.get(
        db=db,
        sample_id=sample_id,
    )

    if not sample:
        logger.error("cannot find sample:{}", sample_id)
        raise LabelUException(
            code=ErrorCode.CODE_55001_SAMPLE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # response
    return SampleResponse(
        id=sample.id,
        inner_id=sample.inner_id,
        state=sample.state,
        data=json.loads(sample.data),
        is_pre_annotated=is_sample_pre_annotated(db=db, task_id=task_id, sample_name=sample.file.filename if sample.file else None),
        file=AttachmentResponse(id=sample.file.id, filename=sample.file.filename, url=sample.file.url) if sample.file else None,
        annotated_count=sample.annotated_count,
        created_at=sample.created_at,
        created_by=UserResp(
            id=sample.owner.id,
            username=sample.owner.username,
        ),
        updated_at=sample.updated_at,
        updaters=[UserResp(
            id=updater.id,
            username=updater.username,
        ) for updater in sample.updaters],
    )


async def patch(
    db: Session,
    task_id: int,
    sample_id: int,
    cmd: PatchSampleCommand,
    current_user: User,
) -> SampleResponse:

    # check task exist
    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        logger.error("cannot find task:{}", task_id)
        raise LabelUException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # get sample
    sample = crud_sample.get(db=db, sample_id=sample_id)
    if not sample:
        logger.error("cannot find sample:{}", sample_id)
        raise LabelUException(
            code=ErrorCode.CODE_55001_SAMPLE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # update
    sample_obj_in = {}
    if cmd.state == SampleState.SKIPPED.value:
        sample_obj_in[TaskSample.state.key] = SampleState.SKIPPED.value
    elif cmd.state == SampleState.NEW.value:
        sample_obj_in[TaskSample.data.key] = json.dumps(cmd.data, ensure_ascii=False)
        sample_obj_in[TaskSample.annotated_count.key] = cmd.annotated_count
        sample_obj_in[TaskSample.state.key] = SampleState.NEW.value
    else:  # can be None, or DONE
        sample_obj_in[TaskSample.data.key] = json.dumps(cmd.data, ensure_ascii=False)
        sample_obj_in[TaskSample.annotated_count.key] = cmd.annotated_count
        sample_obj_in[TaskSample.state.key] = SampleState.DONE.value

    with db.begin():
        # update task status
        if task.status != TaskStatus.FINISHED.value:
            statics = crud_sample.statics(
                db=db, task_ids=[task_id]
            )
            task_obj_in = {Task.status.key: TaskStatus.INPROGRESS.value}
            new_sample_cnt = statics.get(f"{task.id}_{SampleState.NEW.value}", 0)
            if new_sample_cnt == 0 or (
                new_sample_cnt == 1 and sample.state == SampleState.NEW.value
            ):
                task_obj_in[Task.status.key] = TaskStatus.FINISHED.value
            if task.status != task_obj_in[Task.status.key]:
                crud_task.update(db=db, db_obj=task, obj_in=task_obj_in)
        # updaters
        if current_user not in sample.updaters:
            sample.updaters.append(current_user)
        # update task sample result
        updated_sample = crud_sample.update(db=db, db_obj=sample, obj_in=sample_obj_in)
    
    # tell other clients in the same sample page to refresh data
    await sampleConnectionManager.send_message(
        client_id=f"task_{task_id}",
        message=Message(
            type=MessageType.UPDATE,
            data=TaskSampleWsPayload(
                task_id=task_id,
                user_id=current_user.id,
                username=current_user.username,
                sample_id=sample_id,
            )
        )
    )

    # response
    return SampleResponse(
        id=updated_sample.id,
        inner_id=updated_sample.inner_id,
        state=updated_sample.state,
        data=json.loads(updated_sample.data),
        is_pre_annotated=is_sample_pre_annotated(db=db, task_id=task_id, sample_name=sample.file.filename if sample.file else None),
        annotated_count=updated_sample.annotated_count,
        created_at=updated_sample.created_at,
        created_by=UserResp(
            id=updated_sample.owner.id,
            username=updated_sample.owner.username,
        ),
        updated_at=updated_sample.updated_at,
        updaters=[UserResp(
            id=updater.id,
            username=updater.username,
        ) for updater in updated_sample.updaters],
    )


async def delete(
    db: Session, sample_ids: List[int], current_user: User
) -> CommonDataResp:

    with db.begin():
        # delete media
        samples = crud_sample.get_by_ids(db=db, sample_ids=sample_ids)
        attachment_ids = [sample.file_id for sample in samples if sample.file_id]
        attachments = crud_attachment.get_by_ids(db=db, attachment_ids=attachment_ids)
        
        attachments = crud_attachment.get_by_ids(
            db=db, attachment_ids=attachment_ids
        )
        for attachment in attachments:
            file_full_path = Path(settings.MEDIA_ROOT).joinpath(attachment.path)
            os.remove(file_full_path)
        
        crud_sample.delete(db=db, sample_ids=sample_ids)
    # response
    return CommonDataResp(ok=True)


async def create_export_job(
    db: Session,
    task_id: int,
    export_type: ExportType,
    sample_ids: List[int],
    current_user: User,
) -> int:
    """Create an export job and start background processing. Returns job_id immediately."""

    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        raise LabelUException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    with db.begin():
        job = crud_export_job.create(
            db=db,
            task_id=task_id,
            user_id=current_user.id,
            export_type=export_type.value,
            sample_ids=sample_ids,
        )
        job_id = job.id

    # Run blocking export work in a thread pool to avoid blocking the event loop
    asyncio.get_event_loop().run_in_executor(
        None, _run_export_sync, job_id, task_id, export_type, sample_ids
    )
    return job_id


def _run_export_sync(job_id: int, task_id: int, export_type: ExportType, sample_ids: List[int]):
    """Run export in a thread. All operations here are synchronous and blocking."""
    from labelu.internal.common.db import SessionLocal

    db = SessionLocal()
    try:
        job = crud_export_job.get(db=db, job_id=job_id)
        with db.begin():
            crud_export_job.update_status(db, job, ExportStatus.PROCESSING.value)

        task = crud_task.get(db=db, task_id=task_id)
        samples = crud_sample.get_by_ids(db=db, sample_ids=sample_ids)

        data = []
        for sample in samples:
            file_dict = {}
            if sample.file:
                file_dict = {
                    "id": sample.file.id,
                    "filename": sample.file.filename,
                    "url": sample.file.url,
                    "path": sample.file.path if hasattr(sample.file, "path") else "",
                }
            data.append({
                "id": sample.id,
                "inner_id": sample.inner_id,
                "state": sample.state,
                "data": sample.data,
                "annotated_count": sample.annotated_count,
                "file": file_dict,
            })

        out_data_dir = Path(settings.MEDIA_ROOT).joinpath(
            settings.EXPORT_DIR,
            f"task-{task_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[0:8]}",
        )

        file_full_path = converter.convert(
            config=json.loads(task.config),
            input_data=data,
            out_data_dir=out_data_dir,
            out_data_file_name_prefix=task_id,
            format=export_type.value,
        )

        with db.begin():
            crud_export_job.update_status(
                db, job, ExportStatus.COMPLETED.value,
                file_path=str(file_full_path),
                processed_count=len(data),
            )
    except Exception as e:
        logger.error("Export job {} failed: {}", job_id, str(e))
        try:
            job = crud_export_job.get(db=db, job_id=job_id)
            with db.begin():
                crud_export_job.update_status(
                    db, job, ExportStatus.FAILED.value,
                    error_message=str(e),
                )
        except Exception:
            logger.error("Failed to update export job status for job {}", job_id)
    finally:
        db.close()


async def export(
    db: Session,
    task_id: int,
    export_type: ExportType,
    sample_ids: List[int],
    current_user: User,
) -> str:
    """Legacy synchronous export. Kept for backward compatibility."""

    task = crud_task.get(db=db, task_id=task_id)
    samples = crud_sample.get_by_ids(db=db, sample_ids=sample_ids)
    data = []
    for sample in samples:
        file_dict = {}
        if sample.file:
            file_dict = {
                "id": sample.file.id,
                "filename": sample.file.filename,
                "url": sample.file.url,
                "path": sample.file.path if hasattr(sample.file, "path") else "",
            }
        data.append({
            "id": sample.id,
            "inner_id": sample.inner_id,
            "state": sample.state,
            "data": sample.data,
            "annotated_count": sample.annotated_count,
            "file": file_dict,
        })

    # output data path
    out_data_dir = Path(settings.MEDIA_ROOT).joinpath(
        settings.EXPORT_DIR,
        f"task-{task_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{str(uuid.uuid4())[0:8]}",
    )

    # converter to export_type
    file_full_path = converter.convert(
        config=json.loads(task.config),
        input_data=data,
        out_data_dir=out_data_dir,
        out_data_file_name_prefix=task_id,
        format=export_type.value,
    )

    # response
    return file_full_path