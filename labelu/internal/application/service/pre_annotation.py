import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional

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

def read_jsonl_file(db: Session, file_id: int) -> List[dict]:
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

        def validate_sample_name_exists(file_id: int, pre_annotations_dict: Dict[str, List[TaskPreAnnotation]]) -> List[dict]:
            jsonl_content = read_jsonl_file(db, file_id)
            
            for item in jsonl_content:
                sample_name = item.get("sample_name")
                pre_annotations = pre_annotations_dict.get(sample_name, [])
                
                if len(pre_annotations) > 0:
                    raise LabelUException(
                        code=ErrorCode.CODE_55002_SAMPLE_NAME_EXISTS,
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
        
        # Get all pre_annotations in one query
        query_pre_annotations = crud_pre_annotation.list_by_task_id_and_owner_id(db=db, task_id=task_id, owner_id=current_user.id)
        
        pre_annotations_dict = {}
        for pre_annotation in query_pre_annotations:
            jsonl_content = read_jsonl_file(db, pre_annotation.file_id)
            
            for item in jsonl_content:
                sample_name = item.get("sample_name")

                # 如果字典中已经有这个 sample_name，就添加到列表中
                if sample_name in pre_annotations_dict:
                    pre_annotations_dict[sample_name].append(pre_annotation)
                # 否则，创建一个新的列表
                else:
                    pre_annotations_dict[sample_name] = [pre_annotation]
        
        for pre_annotation in cmd:
            validate_sample_name_exists(pre_annotation.file_id, pre_annotations_dict)
        
        pre_annotations = [
            TaskPreAnnotation(
                task_id=task_id,
                file_id=pre_annotation.file_id,
                created_by=current_user.id,
                updated_by=current_user.id,
            )
            for pre_annotation in cmd
        ]
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
        jsonl_content = read_jsonl_file(db, file_id)
        # Filter by sample_name
        result = []
        for item in jsonl_content:
            if sample_name is None or item.get("sample_name") == sample_name:
                result.append(item)
        return result
    
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

async def delete(
    db: Session, pre_annotation_ids: List[int], current_user: User
) -> CommonDataResp:

    with db.begin():
        crud_pre_annotation.delete(db=db, pre_annotation_ids=pre_annotation_ids)
    # response
    return CommonDataResp(ok=True)
