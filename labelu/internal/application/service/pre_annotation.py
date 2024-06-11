import json
from typing import List, Tuple, Optional

from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.application.response.pre_annotation_detail import PreAnnotationDetailResponse
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_pre_annotation, crud_pre_annotation_detail
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

        # if sample_name exists, raise error
        def validate_sample_name_exists(_data: str):
            # data 为 jsonl 字符串，按换行符分割
            jsonl_content = _data.split("\n")
            
            for item in jsonl_content:
                item = json.loads(item)
                sample_name = item.get("sample_name")
                details = crud_pre_annotation_detail.list_by_task_id_and_sample_name(db, task_id, sample_name)
                
                if len(details) > 0:
                    raise LabelUException(
                        code=ErrorCode.CODE_55002_SAMPLE_NAME_EXISTS,
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
        
        for pre_annotation in cmd:
            validate_sample_name_exists(pre_annotation.data)
        
        pre_annotations = [
            TaskPreAnnotation(
                task_id=task_id,
                filename=pre_annotation.filename,
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
    after: Optional[int],
    before: Optional[int],
    pageNo: Optional[int],
    pageSize: int,
    current_user: User,
) -> Tuple[List[PreAnnotationResponse], int]:
    
    try:
    
        results = crud_pre_annotation.list_by(
            db=db,
            task_id=task_id,
            after=after,
            before=before,
            pageNo=pageNo,
            pageSize=pageSize,
            owner_id=current_user.id,
        )
        total = crud_pre_annotation.count(db=db, task_id=task_id, owner_id=current_user.id)

        filtered_pre_annotations = []
        
        for i, item in enumerate(results):
            
            filtered_pre_annotations.append(
                PreAnnotationResponse(
                    id=item.id,
                    filename=item.filename,
                    created_at=item.created_at,
                    details=[
                        PreAnnotationDetailResponse(
                            id=detail.id,
                            sample_name=detail.sample_name,
                            data=detail.data,
                            task_id=detail.task_id,
                            pre_annotation_id=detail.pre_annotation_id, 
                        )
                        for detail in item.details
                        ],
                    created_by=UserResp(
                        id=item.owner.id,
                        username=item.owner.username,
                    ),
                )
            )
    except Exception as e:
        logger.error("list pre_annotation error:{}", e)
        raise LabelUException(
            code=ErrorCode.CODE_50001_INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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
        crud_pre_annotation_detail.delete_by_pre_annotation_ids(db=db, ids=pre_annotation_ids)
    # response
    return CommonDataResp(ok=True)
