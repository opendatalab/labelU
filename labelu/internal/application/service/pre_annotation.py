import json
from datetime import datetime
from typing import List, Tuple, Optional

from pathlib import Path
from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.common.config import settings
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_pre_annotation
from labelu.internal.adapter.persistence import crud_attachment
from labelu.internal.domain.models.user import User
from labelu.internal.domain.models.pre_annotation import TaskPreAnnotation
from labelu.internal.application.command.pre_annotation import CreatePreAnnotationCommand
from labelu.internal.application.response.base import UserResp
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.pre_annotation import CreatePreAnnotationResponse
from labelu.internal.application.response.pre_annotation import PreAnnotationResponse
from labelu.internal.application.response.attachment import AttachmentResponse

async def create(
    db: Session, task_id: int, cmd: List[CreatePreAnnotationCommand], current_user: User
) -> CreatePreAnnotationResponse:
    with db.begin():
        # check task exist
        task = crud_task.get(db=db, task_id=task_id, lock=True)
        if not task:
            logger.error("cannot find task:{}", task_id)
            raise LabelUException(
                code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )

        # TODO: Check if there are any duplicated sample_name exists, if so, raise an error

        pre_annotations = [
            TaskPreAnnotation(
                task_id=task_id,
                file_id=pre_annotation.file_id,
                created_by=current_user.id,
                updated_by=current_user.id,
            )
            for i, pre_annotation in enumerate(cmd)
        ]
        new_samples = crud_pre_annotation.batch(db=db, pre_annotations=pre_annotations)

    # response
    ids = [s.id for s in new_samples]
    return CreatePreAnnotationResponse(ids=ids)


async def list_by(
    db: Session,
    task_id: Optional[int],
    sample_name: Optional[str],
    after: Optional[int],
    before: Optional[int],
    pageNo: Optional[int],
    pageSize: int,
    sorting: Optional[str],
    current_user: User,
) -> Tuple[List[PreAnnotationResponse], int]:

    pre_annotations = crud_pre_annotation.list_by(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
        after=after,
        before=before,
        pageNo=pageNo,
        pageSize=pageSize,
        sorting=sorting,
    )

    total = crud_pre_annotation.count(db=db, task_id=task_id, owner_id=current_user.id)

    def parse_jsonl_file(file_id: int, sample_name: str) -> List[dict]:
        attachment = crud_attachment.get(db, file_id)
        if attachment is None:
            raise LabelUException(status_code=404, code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND)

        attachment_path = attachment.path
        file_full_path = settings.MEDIA_ROOT.joinpath(attachment_path.lstrip("/"))

        try:
            with open(file_full_path, "r", encoding="utf-8") as f:
                data = f.readlines()
        except FileNotFoundError:
            raise LabelUException(status_code=404, code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND)

        # Filter by sample_name
        parsed_data = []
        for line in data:
            line_data = json.loads(line)
            if sample_name is None or line_data.get("sample_name") == sample_name:
                parsed_data.append(line_data)
        return parsed_data
    
    real_sample_name = sample_name[9:] if sample_name else None
    parsed_data_list = [parse_jsonl_file(pre_annotation.file_id, real_sample_name) for pre_annotation in pre_annotations]

    def is_contains_sample_name(inputs: List[dict], sample_name: str) -> bool:
        return any(data.get("sample_name") == sample_name for data in inputs)

    filtered_pre_annotations = []
    for i, pre_annotation in enumerate(pre_annotations):
        if real_sample_name is None or is_contains_sample_name(parsed_data_list[i], real_sample_name):
            filtered_pre_annotations.append(
                PreAnnotationResponse(
                    id=pre_annotation.id,
                    file=AttachmentResponse(id=pre_annotation.file.id, filename=pre_annotation.file.filename, url=pre_annotation.file.url) if pre_annotation.file else None,
                    created_at=pre_annotation.created_at,
                    data=parsed_data_list[i],
                    created_by=UserResp(
                        id=pre_annotation.owner.id,
                        username=pre_annotation.owner.username,
                    ),
                    updated_at=pre_annotation.updated_at,
                    updated_by=UserResp(
                        id=pre_annotation.updater.id,
                        username=pre_annotation.updater.username,
                    ),
                )
            )
    
    return filtered_pre_annotations, total


async def get(
    db: Session, task_id: int, pre_annotation_id: int, sample_id: int, current_user: User
) -> PreAnnotationResponse:
    pre_annotation = crud_pre_annotation.get(
        db=db,
        pre_annotation_id=pre_annotation_id,
    )

    if not pre_annotation:
        logger.error("cannot find pre_annotation: {}", pre_annotation_id)
        raise LabelUException(
            code=ErrorCode.CODE_55001_SAMPLE_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
        
    # response
    return PreAnnotationResponse(
        id=pre_annotation.id,
        file=AttachmentResponse(id=pre_annotation.file.id, filename=pre_annotation.file.filename, url=pre_annotation.file.url),
        created_at=pre_annotation.created_at,
        created_by=UserResp(
            id=pre_annotation.owner.id,
            username=pre_annotation.owner.username,
        ),
        updated_at=pre_annotation.updated_at,
        updated_by=UserResp(
            id=pre_annotation.updater.id,
            username=pre_annotation.updater.username,
        ),
    )

async def delete(
    db: Session, pre_annotation_ids: List[int], current_user: User
) -> CommonDataResp:

    with db.begin():
        crud_pre_annotation.delete(db=db, pre_annotation_ids=pre_annotation_ids)
    # response
    return CommonDataResp(ok=True)
