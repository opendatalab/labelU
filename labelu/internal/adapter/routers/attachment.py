from pathlib import Path
import re
import aiofiles
from sqlalchemy.orm import Session
from fastapi import APIRouter, status, Depends, Security
from fastapi import File, Header, UploadFile
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPAuthorizationCredentials
import mimetypes

from labelu.internal.common import db
from labelu.internal.common.error_code import ErrorCode, LabelUException
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
    
    try:
        full_path = await service.download_attachment(file_path=file_path)
        full_path = Path(full_path) 
    except Exception:
        raise LabelUException(
            code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )
    
    if not full_path.exists():
        raise LabelUException(
            code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # Business logic
    file_size = full_path.stat().st_size
    media_type = mimetypes.guess_type(str(full_path))[0] or "application/octet-stream"
    
    if not range:
        return FileResponse(
            path=str(full_path),
            media_type=media_type,
            headers={"Accept-Ranges": "bytes"}
        )
        
    try:
        range_match = re.match(r'bytes=(\d+)-(\d*)', range)
        if not range_match:
            raise ValueError("Invalid range format")
        
        start = int(range_match.group(1))
        end_str = range_match.group(2)
        end = int(end_str) if end_str else min(start + 1024 * 1024, file_size - 1)
        
        # 验证范围
        if start < 0 or start >= file_size:
            raise ValueError(f"Start position {start} out of bounds")
        
        if end >= file_size:
            end = file_size - 1
        
        content_length = end - start + 1
        
    except ValueError:
        return FileResponse(
            path=str(full_path),
            media_type=media_type,
            headers={"Accept-Ranges": "bytes"}
        )
        
        
    async def file_stream():
        async with aiofiles.open(str(full_path), 'rb') as f:
            await f.seek(start)
            remaining = content_length
            chunk_size = min(64 * 1024, remaining)
            
            while remaining > 0:
                chunk = await f.read(min(chunk_size, remaining))
                if not chunk:
                    break
                remaining -= len(chunk)
                yield chunk
    
    headers = {
        "Accept-Ranges": "bytes",
        "Content-Range": f"bytes {start}-{end}/{file_size}",
        "Content-Length": str(content_length),
    }
    
    return StreamingResponse(
        file_stream(),
        status_code=206,
        media_type=media_type,
        headers=headers
    )


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
