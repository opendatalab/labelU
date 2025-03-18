import re
import aiofiles
import os
from PIL import Image
from pathlib import Path

from loguru import logger
from fastapi import status
from sqlalchemy.orm import Session

from labelu.internal.common.config import settings
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.domain.models.user import User
from labelu.internal.domain.models.attachment import TaskAttachment
from labelu.internal.adapter.persistence import crud_task
from labelu.internal.adapter.persistence import crud_attachment
from labelu.internal.application.command.attachment import AttachmentCommand
from labelu.internal.application.command.attachment import AttachmentDeleteCommand
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.attachment import AttachmentResponse


async def create(
    db: Session, task_id: int, cmd: AttachmentCommand, current_user: User
) -> AttachmentResponse:

    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        logger.error("cannot find task: {}", task_id)
        raise LabelUException(
            code=ErrorCode.CODE_50002_TASK_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

        # file relative path
    path_filename = cmd.file.filename.split("/")
    #  filename = str(uuid.uuid4())[0:8] + "-" + path_filename[-1] NOTE: If you want keep filename safe, you can use uuid as filename 
    filename = path_filename[-1]
    sanitized = re.sub(r'%', '_pct_', filename)
    sanitized = re.sub(r'[\\/*?:"<>|]', '_', sanitized)
    path = "/".join(path_filename[:-1])
    attachment_relative_base_dir = Path(settings.UPLOAD_DIR).joinpath(
        str(task_id), path
    )
    attachment_relative_path = str(attachment_relative_base_dir.joinpath(sanitized))

    # file full path
    attachment_full_base_dir = Path(settings.MEDIA_ROOT).joinpath(
        attachment_relative_base_dir
    )
    attachment_full_path = Path(settings.MEDIA_ROOT).joinpath(
        attachment_relative_path
    )

    # check file exist
    if attachment_full_path.exists():
        logger.error("file already exists:{}", attachment_full_path)
        raise LabelUException(
            code=ErrorCode.CODE_51002_TASK_ATTACHMENT_ALREADY_EXISTS,
            status_code=status.HTTP_400_BAD_REQUEST,
        )
        
    # create dicreatory
    attachment_full_base_dir.mkdir(parents=True, exist_ok=True)
    
    CHUNK_SIZE = 8 * 1024 * 1024  # 8MB
    logger.info(attachment_full_path)
    try:
        async with aiofiles.open(attachment_full_path, "wb") as out_file:
            total_size = 0
            while True:
                chunk = await cmd.file.read(CHUNK_SIZE)
                if not chunk:
                    break
                await out_file.write(chunk)
                total_size += len(chunk)
                logger.debug(f"{total_size} bytes written")

        logger.info(f"File saved: {attachment_full_path}, size: {total_size} bytes")
    except Exception as e:
        if attachment_full_path.exists():
            os.remove(attachment_full_path)
        logger.error(f"Upload failed: {str(e)}")
        raise LabelUException(
            code=ErrorCode.CODE_51000_CREATE_ATTACHMENT_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message=f"Upload failed: {str(e)}"
        )

    # create thumbnail for image
    if cmd.file.content_type.startswith("image/"):
        tumbnail_full_path = Path(
            f"{attachment_full_path.parent}/{attachment_full_path.stem}-thumbnail{attachment_full_path.suffix}"
        )
        logger.info(tumbnail_full_path)
        image = Image.open(attachment_full_path)
        image.thumbnail(
            (
                round(image.width / image.height * settings.THUMBNAIL_HEIGH_PIXEL),
                settings.THUMBNAIL_HEIGH_PIXEL,
            ),
        )
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.save(tumbnail_full_path)

    # check file already saved
    if not attachment_full_path.exists() or (
        cmd.file.content_type.startswith("image/") and not tumbnail_full_path.exists()
    ):
        logger.error(
            "cannot find saved images, path is:{}, image content-type is:{}, thumbnail path is:{}",
            attachment_full_path,
            cmd.file.content_type,
            tumbnail_full_path,
        )
        raise LabelUException(
            code=ErrorCode.CODE_51000_CREATE_ATTACHMENT_ERROR,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    attachment_url_path = attachment_relative_path.replace("\\", "/")
    attachment_api_url = f"{settings.API_V1_STR}/tasks/attachment/{attachment_url_path}"
    # add a task file record
    with db.begin():
        attachment = crud_attachment.create(
            db=db,
            attachment=TaskAttachment(
                path=attachment_url_path,
                url=attachment_api_url,
                filename=sanitized,
                created_by=current_user.id,
                updated_by=current_user.id,
                task_id=task_id,
            ),
        )

    # response
    return AttachmentResponse(
        id=attachment.id,
        url=attachment_api_url,
        filename=sanitized,
    )


async def download_attachment(file_path: str) -> str:

    # check file exist
    file_full_path = settings.MEDIA_ROOT.joinpath(file_path.lstrip("/"))
    if not file_full_path.is_file() or not file_full_path.exists():
        logger.error("attachment not found:{}", file_full_path)
        raise LabelUException(
            code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    # response
    return file_full_path


async def delete(
    db: Session, task_id: int, cmd: AttachmentDeleteCommand, current_user: User
) -> CommonDataResp:

    # get task
    task = crud_task.get(db=db, task_id=task_id)
    if not task:
        logger.error("cannot find task:{}", task_id)
        raise LabelUException(
            code=ErrorCode.CODE_51001_TASK_ATTACHMENT_NOT_FOUND,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    if task.created_by != current_user.id:
        logger.error(
            "cannot delete attachment, the task owner is:{}, the delete operator is:{}",
            task.created_by,
            current_user.id,
        )
        raise LabelUException(
            code=ErrorCode.CODE_30001_NO_PERMISSION,
            status_code=status.HTTP_403_FORBIDDEN,
        )

    # delete media
    try:
        attachments = crud_attachment.get_by_ids(
            db=db, attachment_ids=cmd.attachment_ids
        )
        for attachment in attachments:
            file_full_path = Path(settings.MEDIA_ROOT).joinpath(attachment.path)
            os.remove(file_full_path)
    except Exception as e:
        logger.error(e)

    # delete
    with db.begin():
        crud_attachment.delete(db=db, attachment_ids=cmd.attachment_ids)

    # response
    return CommonDataResp(ok=True)
