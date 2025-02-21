import json
import os
from pathlib import Path
from typing import List, Tuple, Optional

from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.common.config import settings
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
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
from labelu.internal.application.response.attachment import AttachmentResponse

def read_pre_annotation_file(attachment: TaskAttachment) -> List[dict]:
    if attachment is None:
        return []

    attachment_path = attachment.path
    file_full_path = settings.MEDIA_ROOT.joinpath(attachment_path.lstrip("/"))
    
    # check if the file exists
    if not file_full_path.exists() or (not attachment.filename.endswith('.jsonl') and not attachment.filename.endswith('.json')):
        return []

    try:
        if attachment.filename.endswith('.jsonl'):
            with open(file_full_path, "r", encoding="utf-8") as f:
                data = f.readlines()
                return [json.loads(line) for line in data]
        else:
            with open(file_full_path, "r", encoding="utf-8") as f:    
                # parse result
                parsed_data = json.load(f)
                
                return [{**item, "result": json.loads(item["result"])} for item in parsed_data]
    
    except FileNotFoundError:
        raise LabelUException(status_code=404, code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND)

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
            file=AttachmentResponse(id=pre_annotation.file.id, filename=pre_annotation.file.filename, url=pre_annotation.file.url) if pre_annotation.file else None,
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
) -> Tuple[List[TaskAttachment], int]:
    try:
        pre_annotations = crud_pre_annotation.list_by_task_id_and_owner_id(db=db, task_id=task_id)
        file_ids = [pre_annotation.file_id for pre_annotation in pre_annotations]
        
        attachments, total = crud_attachment.list_by(db=db, ids=file_ids, after=after, before=before, page=page, size=size, sorting=sorting)
        _attachment_ids = [attachment.id for attachment in attachments]
        sample_names_those_has_pre_annotations = []
        
        for pre_annotation in pre_annotations:
            if pre_annotation.file_id in _attachment_ids and pre_annotation.sample_name is not None:
                sample_names_those_has_pre_annotations.append(pre_annotation.sample_name)

        return [
            PreAnnotationFileResponse(
                id=attachment.id,
                url=attachment.url,
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
        file=AttachmentResponse(id=pre_annotation.file.id, filename=pre_annotation.file.filename, url=pre_annotation.file.url) if pre_annotation.file else None,
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
    with db.begin():
        attachments = crud_attachment.get_by_ids(
            db=db, attachment_ids=[file_id]
        )
        
        for attachment in attachments:
            file_full_path = Path(settings.MEDIA_ROOT).joinpath(attachment.path)
            os.remove(file_full_path)
            
        pre_annotations = crud_pre_annotation.list_by_task_id_and_file_id(db=db, task_id=task_id, file_id=file_id)
        pre_annotation_ids = [pre_annotation.id for pre_annotation in pre_annotations]
        
        crud_pre_annotation.delete(db=db, pre_annotation_ids=pre_annotation_ids)
        crud_attachment.delete(db=db, attachment_ids=[file_id])
            
    # response
    return CommonDataResp(ok=True)

async def delete(
    db: Session, pre_annotation_ids: List[int], current_user: User
) -> CommonDataResp:

    with db.begin():
        crud_pre_annotation.delete(db=db, pre_annotation_ids=pre_annotation_ids)
    # response
    return CommonDataResp(ok=True)
