from typing import List, Union

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, status, Security
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.application.response.pre_annotation_detail import PreAnnotationDetailResponse
from labelu.internal.common import db
from labelu.internal.common.security import security
from labelu.internal.domain.models.user import User
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import pre_annotation_detail as service
from labelu.internal.application.command.pre_annotation_detail import DeletePreAnnotationDetailCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.base import MetaData
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.base import OkRespWithMeta


router = APIRouter(prefix="/tasks", tags=["pre_annotations"])


@router.get(
    "/{task_id}/pre_annotation_details",
    response_model=OkRespWithMeta[List[PreAnnotationDetailResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_by(
    task_id: int,
    sample_name: str = Query(default=None, min_length=1, max_length=255),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a pre annotation detail result.
    """
    # business logic
    data, total = await service.list_by(
        db=db,
        task_id=task_id,
        sample_name=sample_name,
        current_user=current_user,
    )

    # response
    meta_data = MetaData(total=total, page=0, size=len(data))
    return OkRespWithMeta[List[PreAnnotationDetailResponse]](meta_data=meta_data, data=data)


@router.get(
    "/{task_id}/pre_annotation_detail",
    response_model=OkRespWithMeta[PreAnnotationDetailResponse],
    status_code=status.HTTP_200_OK,
)
async def get(
    task_id: int,
    sample_name: str = Query(default=None, min_length=1, max_length=255),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a pre annotation detail result.
    """
    # business logic
    data = await service.get(
        db=db,
        task_id=task_id,
        sample_name=sample_name,
        current_user=current_user,
    )

    return OkResp[PreAnnotationDetailResponse](data=data)


@router.delete(
    "/{task_id}/pre_annotation_detail",
    response_model=OkResp[CommonDataResp],
    status_code=status.HTTP_200_OK,
)
async def delete(
    cmd: DeletePreAnnotationDetailCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    delete a annotation.
    """

    # business logic
    data = await service.delete(
        db=db, pre_annotation_ids=cmd.pre_annotation_ids, current_user=current_user
    )

    # response
    return OkResp[CommonDataResp](data=data)

