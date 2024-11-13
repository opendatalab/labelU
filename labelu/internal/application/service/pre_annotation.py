import json
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

def read_jsonl_file(attachment: TaskAttachment) -> List[dict]:
    if attachment is None:
        return []

    attachment_path = attachment.path
    file_full_path = settings.MEDIA_ROOT.joinpath(attachment_path.lstrip("/"))
    
    # check if the file exists
    if not file_full_path.exists() or not attachment.filename.endswith('.jsonl'):
        return []

    try:
        with open(file_full_path, "r", encoding="utf-8") as f:
            data = f.readlines()
    except FileNotFoundError:
        raise LabelUException(status_code=404, code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND)

    parsed_data = [json.loads(line) for line in data]
    return parsed_data

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
            jsonl_file = crud_attachment.get(db, pre_annotation.file_id)
            exist_pre_annotations = crud_pre_annotation.list_by_task_id_and_owner_id_and_sample_name(db=db, task_id=task_id, owner_id=current_user.id, sample_name=jsonl_file.filename)
            
            if len(exist_pre_annotations) > 0:
                raise LabelUException(
                    code=ErrorCode.CODE_55002_SAMPLE_NAME_EXISTS,
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
            
            jsonl_contents = read_jsonl_file(jsonl_file)
            
            for jsonl_content in jsonl_contents:
                pre_annotations.append(
                    TaskPreAnnotation(
                        task_id=task_id,
                        file_id=pre_annotation.file_id,
                        sample_name=jsonl_content.get("sample_name"),
                        data=json.dumps(jsonl_content, ensure_ascii=False),
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
    pageNo: Optional[int],
    pageSize: int,
    sorting: Optional[str],
    current_user: User,
) -> Tuple[List[PreAnnotationResponse], int]:
    
    pre_annotations, total = crud_pre_annotation.list_by(
        db=db,
        task_id=task_id,
        owner_id=current_user.id,
        after=after,
        before=before,
        pageNo=pageNo,
        sample_name=sample_name,
        pageSize=None if sample_name else pageSize,
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
    pageNo: Optional[int],
    pageSize: int,
    sorting: Optional[str],
    current_user: User,
) -> Tuple[List[TaskAttachment], int]:
    pre_annotations = crud_pre_annotation.list_by_task_id_and_owner_id(db=db, task_id=task_id, owner_id=current_user.id)
    file_ids = [pre_annotation.file_id for pre_annotation in pre_annotations]
    
    attachments, total = crud_attachment.list_by(db=db, ids=file_ids, after=after, before=before, pageNo=pageNo, pageSize=pageSize, sorting=sorting)

    return [
        PreAnnotationFileResponse(
            id=attachment.id,
            url=attachment.url,
            filename=attachment.filename,
            sample_names=[pre_annotation.sample_name for pre_annotation in pre_annotations if pre_annotation.file_id == attachment.id]
        )
        for attachment in attachments
    ], total


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
        pre_annotations = crud_pre_annotation.list_by_task_id_and_owner_id_and_sample_name(db=db, task_id=task_id, owner_id=current_user.id, sample_name=crud_attachment.get(db, file_id).filename)
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
