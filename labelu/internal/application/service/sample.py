import json
from typing import List
from pathlib import Path

from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.domain.models.user import User
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import UnicornException
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_sample
from labelu.internal.domain.models.sample import TaskSample
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
        raise UnicornException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUN,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    samples = [
        TaskSample(
            task_id=task_id,
            task_attachment_id=str(sample.attachement_ids),
            created_by=current_user.id,
            updated_by=current_user.id,
            data=json.dumps(sample.data),
        )
        for sample in cmd
    ]

    new_samples = crud_sample.batch(db=db, samples=samples)

    # response
    ids = [s.id for s in new_samples]
    return CreateSampleResponse(ids=ids)


async def list_by(
    db: Session, after: int, before: int, pageNo: int, pageSize: int, current_user: User
) -> List[SampleResponse]:

    samples = crud_sample.list_by(
        db=db,
        owner_id=current_user.id,
        after=after,
        before=before,
        pageNo=pageNo,
        pageSize=pageSize,
    )

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
    ]


async def get(db: Session, sample_id: int, current_user: User) -> SampleResponse:
    sample = crud_sample.get(
        db=db,
        sample_id=sample_id,
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
    db: Session, sample_id: int, cmd: PatchSampleCommand, current_user: User
) -> SampleResponse:

    # get sample
    sample = crud_sample.get(db=db, sample_id=sample_id)
    if not sample:
        raise UnicornException(
            code=ErrorCode.CODE_55001_SAMPLE_NOT_FOUN,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # update
    obj_in = cmd.dict(exclude_unset=True)
    if cmd.state:
        obj_in[TaskSample.state.key] = cmd.state
        obj_in[TaskSample.data.key] = json.dumps(dict())
    else:
        obj_in[TaskSample.data.key] = json.dumps(cmd.data)
        obj_in[TaskSample.annotated_count.key] = cmd.annotated_count
    updated_sample = crud_sample.update(db=db, db_obj=sample, obj_in=obj_in)

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

    crud_sample.delete(db=db, sample_ids=sample_ids)
    # response
    return CommonDataResp(ok=True)


async def export(
    db: Session,
    task_id: int,
    export_type: int,
    sample_ids: List[int],
    current_user: User,
) -> str:

    # response
    return Path()
