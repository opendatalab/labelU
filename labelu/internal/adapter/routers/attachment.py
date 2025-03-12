from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Security
from fastapi import File, Header, Response, UploadFile
from fastapi.responses import FileResponse
from fastapi.security import HTTPAuthorizationCredentials
import mimetypes
import os

from labelu.internal.common import db
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
    
    return data

@router.get(
    "/partial/{file_path:path}",
    response_class=FileResponse,
    status_code=status.HTTP_200_OK,
)
async def get_content(file_path: str, range: str = Header(None)):
    """
    partial content
    """

    # Business logic
    full_path = await service.download_attachment(file_path=file_path)
    CHUNK_SIZE = 1024 * 1024
    full_size = os.path.getsize(full_path)
    start, end = range.replace("bytes=", "").split("-")
    start = int(start)
    end = int(end) if end else min(start + CHUNK_SIZE, full_size) - 1
    media_type = mimetypes.guess_type(full_path)[0]
    # TODO 不知为何到最后range阶段视频播放失效，先加上这个处理取消byte range暂时解决
    if full_size - end == 1:
        return full_path
    
    with open(full_path, 'rb') as video:
        video.seek(start)
        data = video.read(end - start)
        file_size = str(full_path.stat().st_size)
        # 视频或音频标注时，需要支持快进等选定播放时间点，因此需要手动增加以下响应头部
        headers = {"Accept-Ranges": "bytes", "Content-Range": f"bytes {str(start)}-{str(end)}/{file_size}"}
    return Response(data, headers=headers, media_type=media_type, status_code=206)


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
