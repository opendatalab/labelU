import json
import os
from typing import List, Tuple, Optional

from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.common.db import begin_transaction
from labelu.internal.common.config import settings
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.common.storage import (
    build_attachment_api_path,
    build_partial_api_path,
    build_thumbnail_key,
    get_storage_backend,
)
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_pre_annotation
from labelu.internal.adapter.persistence import crud_attachment
from labelu.internal.domain.models.attachment import TaskAttachment
from labelu.internal.domain.models.user import User
from labelu.internal.domain.models.pre_annotation import TaskPreAnnotation
from labelu.internal.application.command.pre_annotation import CreatePreAnnotationCommand
from labelu.internal.application.response.base import UserResp
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.pre_annotation import CreatePreAnnotationResponse, PreAnnotationFileResponse
from labelu.internal.application.response.pre_annotation import PreAnnotationResponse
from labelu.internal.application.service.attachment import build_attachment_response


def read_pre_annotation_file(attachment: TaskAttachment) -> List[dict]:
    if attachment is None:
        return []

    storage = get_storage_backend()
    
    # check if the file exists
    if not storage.exists(attachment.path) or (not attachment.filename.endswith('.jsonl') and not attachment.filename.endswith('.json')):
        return []

    try:
        if attachment.filename.endswith('.jsonl'):
            data = storage.read_text(attachment.path, encoding="utf-8").splitlines()
            return [json.loads(line) for line in data if line.strip()]
        else:
            parsed_data = json.loads(storage.read_text(attachment.path, encoding="utf-8"))
            return [{**item, "result": json.loads(item["result"])} for item in parsed_data]
    
    except FileNotFoundError:
        raise LabelUException(status_code=404, code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND)

async def create(
    db: Session, task_id: int, cmd: List[CreatePreAnnotationCommand], current_user: User
) -> CreatePreAnnotationResponse:
    with begin_transaction(db):
        # check task exist
        task = crud_task.get(db=db, task_id=task_id, lock=True)
        if not task:
            logger.error("cannot find task:{}", task_id)
            raise LabelUException(
                code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        pre_annotations = []
        for pre_annotation in cmd:
            pre_annotation_file = crud_attachment.get(db, pre_annotation.file_id)
            pre_annotation_contents = read_pre_annotation_file(pre_annotation_file)
            
            for _item in pre_annotation_contents:
                sample_name = _item.get("sample_name") if pre_annotation_file.filename.endswith(".jsonl") else _item.get("fileName")
                exist_pre_annotations = crud_pre_annotation.list_by_task_id_and_owner_id_and_sample_name(db=db, task_id=task_id, sample_name=sample_name)
                
                if len(exist_pre_annotations) > 0:
                    raise LabelUException(
                        code=ErrorCode.CODE_55002_SAMPLE_NAME_EXISTS,
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                    
                pre_annotations.append(
                    TaskPreAnnotation(
                        task_id=task_id,
                        file_id=pre_annotation.file_id,
                        sample_name=sample_name,
                        data=json.dumps(_item, ensure_ascii=False),
                        created_by=current_user.id,
                        updated_by=current_user.id,
                    )
                )
        
        new_pre_annotations = crud_pre_annotation.batch(db=db, pre_annotations=pre_annotations)

    # response
    ids = [s.id for s in new_pre_annotations]
    return CreatePreAnnotationResponse(ids=ids)


async def list_by(
    db: Session,
    task_id: Optional[int],
    sample_name: Optional[str],
    after: Optional[int],
    before: Optional[int],
    page: Optional[int],
    size: int,
    sorting: Optional[str],
    current_user: User,
) -> Tuple[List[PreAnnotationResponse], int]:
    
    pre_annotations, total = crud_pre_annotation.list_by(
        db=db,
        task_id=task_id,
        after=after,
        before=before,
        page=page,
        sample_name=sample_name,
        size=None if sample_name else size,
        sorting=sorting,
    )
    
    return [
        PreAnnotationResponse(
            id=pre_annotation.id,
            data=pre_annotation.data,
            file=build_attachment_response(pre_annotation.file),
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
        ) for pre_annotation in pre_annotations
    ], total

async def list_pre_annotation_files(
    db: Session,
    task_id: Optional[int],
    after: Optional[int],
    before: Optional[int],
    page: Optional[int],
    size: int,
    sorting: Optional[str],
    current_user: User,
) -> Tuple[List[TaskAttachment], int]:
    try:
        pre_annotations = crud_pre_annotation.list_by_task_id_and_owner_id_lightweight(db=db, task_id=task_id, owner_id=current_user.id)
        file_ids = [pre_annotation['file_id'] for pre_annotation in pre_annotations]
        
        attachments, total = crud_attachment.list_by(db=db, ids=file_ids, after=after, before=before, page=page, size=size, sorting=sorting)
        _attachment_ids = [attachment.id for attachment in attachments]
        sample_names_those_has_pre_annotations = []
        
        for pre_annotation in pre_annotations:
            if pre_annotation['file_id'] in _attachment_ids and pre_annotation['sample_name'] is not None:
                sample_names_those_has_pre_annotations.append(pre_annotation['sample_name'])

        storage = get_storage_backend()
        return [
            PreAnnotationFileResponse(
                id=attachment.id,
                url=(storage.get_read_url(attachment.path) if storage.is_remote else attachment.url),
                thumbnail_url=(
                    storage.get_read_url(build_thumbnail_key(attachment.path))
                    if storage.is_remote
                    else build_attachment_api_path(build_thumbnail_key(attachment.path))
                ),
                stream_url=(
                    storage.get_read_url(attachment.path)
                    if storage.is_remote
                    else build_partial_api_path(attachment.path)
                ),
                storage_backend=storage.backend_name,
                filename=attachment.filename,
                sample_names=sample_names_those_has_pre_annotations,
            )
            for attachment in attachments
        ], total
        
    except Exception as e:
        logger.error("list pre annotation files error: {}", e)
        raise LabelUException(
            code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )


async def get(
    db: Session, task_id: int, pre_annotation_id: int, current_user: User
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
        file=build_attachment_response(pre_annotation.file),
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
    
async def delete_pre_annotation_file(
    db: Session, task_id: int, file_id: int, current_user: User
) -> CommonDataResp:
    storage = get_storage_backend()
    with begin_transaction(db):
        task = crud_task.get(db=db, task_id=task_id, lock=True)
        if not task:
            logger.error("cannot find task:{}", task_id)
            raise LabelUException(
                code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        attachments = crud_attachment.get_by_ids(
            db=db, attachment_ids=[file_id]
        )

        if len(attachments) == 0:
            raise LabelUException(
                code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND,
                status_code=status.HTTP_404_NOT_FOUND,
            )
        
        for attachment in attachments:
            storage.delete(attachment.path)
            thumbnail_key = build_thumbnail_key(attachment.path)
            if storage.exists(thumbnail_key):
                storage.delete(thumbnail_key)
            
        pre_annotations = crud_pre_annotation.list_by_task_id_and_file_id(db=db, task_id=task_id, file_id=file_id)
        pre_annotation_ids = [pre_annotation.id for pre_annotation in pre_annotations]
        
        crud_pre_annotation.delete(db=db, pre_annotation_ids=pre_annotation_ids)
        crud_attachment.delete(db=db, attachment_ids=[file_id])
            
    # response
    return CommonDataResp(ok=True)

async def delete(
    db: Session, pre_annotation_ids: List[int], current_user: User
) -> CommonDataResp:

    with begin_transaction(db):
        crud_pre_annotation.delete(db=db, pre_annotation_ids=pre_annotation_ids)
    # response
    return CommonDataResp(ok=True)
