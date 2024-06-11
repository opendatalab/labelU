from typing import List, Tuple, Optional

from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.application.response.pre_annotation_detail import (
    PreAnnotationDetailResponse,
)
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.adapter.persistence import (
    crud_pre_annotation,
    crud_pre_annotation_detail,
)
from labelu.internal.domain.models.user import User

from labelu.internal.application.response.base import CommonDataResp


async def list_by(
    db: Session,
    task_id: Optional[int],
    current_user: User,
) -> Tuple[List[PreAnnotationDetailResponse], int]:
    try:
        results = crud_pre_annotation_detail.list_by_task_id_and_sample_name(
            db=db,
            task_id=task_id,
            owner_id=current_user.id,
        )
        total = crud_pre_annotation.count(
            db=db, task_id=task_id, owner_id=current_user.id
        )

        details = []

        for i, item in enumerate(results):
            details.append(
                PreAnnotationDetailResponse(
                    id=item.id,
                    sample_name=item.sample_name,
                    data=item.data,
                    task_id=item.task_id,
                    pre_annotation_id=item.pre_annotation_id,
                )
            )
    except Exception as e:
        logger.error("list pre_annotation error:{}", e)
        raise LabelUException(
            code=ErrorCode.CODE_50001_INTERNAL_SERVER_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    return details, total


async def get(
    db: Session, task_id: int, sample_name: str, current_user: User
) -> PreAnnotationDetailResponse:
    detail = crud_pre_annotation_detail.get(
        db=db,
        task_id=task_id,
        sample_name=sample_name,
    )

    if not detail:
        logger.error("cannot find pre_annotation detail: {}", task_id, sample_name)
        raise LabelUException(
            code=ErrorCode.CODE_56001_PRE_ANNOTATION_DETAIL_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # response
    return PreAnnotationDetailResponse(
        id=detail.id,
        sample_name=detail.sample_name,
        data=detail.data,
        task_id=detail.task_id,
        pre_annotation_id=detail.pre_annotation_id,
    )


async def delete(
    db: Session, pre_annotation_id: int, current_user: User
) -> CommonDataResp:
    with db.begin():
        crud_pre_annotation_detail.delete_by_pre_annotation_id(
            db=db, pre_annotation_id=pre_annotation_id
        )
    # response
    return CommonDataResp(ok=True)
