from sqlalchemy.orm import Session
from fastapi import APIRouter, Form, status, Depends, Security
from fastapi import File, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.common import db
from labelu.internal.common.config import settings
from labelu.internal.common.security import security
from labelu.internal.domain.models.user import User
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import attachment as service
from labelu.internal.application.command.attachment import AttachmentCommand
from labelu.internal.application.command.attachment import AttachmentDeleteCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.attachment import AttachmentResponse


router = APIRouter(prefix="/tasks", tags=["attachments"])


@router.post(
    "/{task_id}/attachments",
    response_model=OkResp[AttachmentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    task_id: int,
    file: UploadFile = File(...),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create attechment as annnotation sample.
    """
    # business logic
    cmd = AttachmentCommand(file=file)
    data = await service.create(
        db=db, task_id=task_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[AttachmentResponse](data=data)


@router.get(
    "/attachment/{file_path:path}",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
)
async def download_attachment(file_path: str):
    """
    download attachment.
    """

    # business logic
    data = await service.download_attachment(file_path=file_path)

    # response
    return data


@router.delete(
    "/{task_id}/attachments",
    response_model=OkResp[CommonDataResp],
    status_code=status.HTTP_200_OK,
)
async def delete(
    task_id: int,
    cmd: AttachmentDeleteCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    delete task.
    """

    # business logic
    data = await service.delete(
        db=db, task_id=task_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[CommonDataResp](data=data)
