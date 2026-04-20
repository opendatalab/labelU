from typing import List, Union
from pathlib import Path

from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, Query, status, Security
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials

from labelu.internal.common import db as db_module
from labelu.internal.common.security import security
from labelu.internal.common.error_code import ErrorCode
from labelu.internal.common.error_code import LabelUException
from labelu.internal.domain.models.user import User
from labelu.internal.dependencies.user import get_current_user
from labelu.internal.application.service import sample as service
from labelu.internal.application.service import auto_label as auto_label_service
from labelu.internal.application.command.auto_label import AutoLabelCommand
from labelu.internal.application.command.sample import ExportType
from labelu.internal.application.command.sample import PatchSampleCommand
from labelu.internal.application.command.sample import CreateSampleCommand
from labelu.internal.application.command.sample import DeleteSampleCommand
from labelu.internal.application.command.sample import ExportSampleCommand
from labelu.internal.application.command.datasource import ImportS3SamplesCommand
from labelu.internal.application.response.base import OkResp
from labelu.internal.application.response.base import MetaData
from labelu.internal.application.response.base import CommonDataResp
from labelu.internal.application.response.base import OkRespWithMeta
from labelu.internal.application.response.sample import SampleResponse
from labelu.internal.application.response.sample import CreateSampleResponse
from labelu.internal.application.response.auto_label import AutoLabelResponse
from labelu.internal.application.response.export import ExportJobResponse
from labelu.internal.adapter.persistence import crud_export_job
from labelu.internal.common.storage import get_storage_backend


router = APIRouter(prefix="/tasks", tags=["samples"])


def _export_progress(sample_count: int, processed_count: int, status: str) -> tuple[int | None, str | None]:
    if status not in {"COMPLETED", "FAILED"}:
        return None, None
    skipped_count = max(sample_count - processed_count, 0)
    if skipped_count == 0:
        return 0, None
    return skipped_count, (
        f"Requested {sample_count} samples, exported {processed_count}, skipped {skipped_count}."
    )


@router.post(
    "/{task_id}/samples",
    response_model=OkResp[CreateSampleResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create(
    task_id: int,
    cmd: List[CreateSampleCommand],
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create a sample.
    """

    # business logic
    data = await service.create(
        db=db, task_id=task_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[CreateSampleResponse](data=data)


@router.get(
    "/{task_id}/samples",
    response_model=OkRespWithMeta[List[SampleResponse]],
    status_code=status.HTTP_200_OK,
)
async def list_by(
    task_id: int,
    after: Union[int, None] = Query(default=None, gt=0),
    before: Union[int, None] = Query(default=None, gt=0),
    page: Union[int, None] = Query(default=None, ge=0),
    size: Union[int, None] = 100,
    sort: Union[str, None] = Query(
        default=None, pattern="(annotated_count|state|inner_id|updated_at):(desc|asc)"
    ),
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a annotation result.
    """

    if len([i for i in (after, before, page) if i != None]) != 1:
        raise LabelUException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code=ErrorCode.CODE_55000_SAMPLE_LIST_PARAMETERS_ERROR,
        )

    # business logic
    data, total = await service.list_by(
        db=db,
        task_id=task_id,
        after=after,
        before=before,
        page=page,
        size=size,
        sorting=sort,
    )

    # response
    meta_data = MetaData(total=total, page=page, size=len(data))
    return OkRespWithMeta[List[SampleResponse]](meta_data=meta_data, data=data)


@router.get(
    "/{task_id}/samples/{sample_id}",
    response_model=OkResp[SampleResponse],
    status_code=status.HTTP_200_OK,
)
async def get(
    task_id: int,
    sample_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get a annotation result.
    """

    # business logic
    data = await service.get(
        db=db, task_id=task_id, sample_id=sample_id
    )

    # response
    return OkResp[SampleResponse](data=data)


@router.patch(
    "/{task_id}/samples/{sample_id}",
    response_model=OkResp[SampleResponse],
    status_code=status.HTTP_200_OK,
)
async def update(
    task_id: int,
    sample_id: int,
    cmd: PatchSampleCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    update a annotation.
    """

    # business logic
    data = await service.patch(
        db=db, task_id=task_id, sample_id=sample_id, cmd=cmd, current_user=current_user
    )

    # response
    return OkResp[SampleResponse](data=data)


@router.post(
    "/{task_id}/samples/{sample_id}/auto_label",
    response_model=OkResp[AutoLabelResponse],
    status_code=status.HTTP_200_OK,
)
async def auto_label(
    task_id: int,
    sample_id: int,
    cmd: AutoLabelCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    data = await auto_label_service.create(
        db=db,
        task_id=task_id,
        sample_id=sample_id,
        cmd=cmd,
        current_user=current_user,
    )
    return OkResp[AutoLabelResponse](data=data)


@router.post(
    "/{task_id}/samples/import_s3",
    response_model=OkResp[CreateSampleResponse],
    status_code=status.HTTP_201_CREATED,
)
async def import_s3(
    task_id: int,
    cmd: ImportS3SamplesCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    data = await service.import_from_s3(
        db=db, task_id=task_id, cmd=cmd, current_user=current_user,
    )
    return OkResp[CreateSampleResponse](data=data)


@router.delete(
    "/{task_id}/samples",
    response_model=OkResp[CommonDataResp],
    status_code=status.HTTP_200_OK,
)
async def delete(
    cmd: DeleteSampleCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    delete a annotation.
    """

    # business logic
    data = await service.delete(
        db=db, sample_ids=cmd.sample_ids, current_user=current_user
    )

    # response
    return OkResp[CommonDataResp](data=data)


@router.post(
    "/{task_id}/samples/export",
    response_model=OkResp[ExportJobResponse],
    status_code=status.HTTP_200_OK,
)
async def export(
    task_id: int,
    export_type: ExportType,
    cmd: ExportSampleCommand,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create an async export job.
    """

    job_id = await service.create_export_job(
        db=db,
        task_id=task_id,
        export_type=export_type,
        sample_ids=cmd.sample_ids,
        current_user=current_user,
    )

    return OkResp[ExportJobResponse](data=ExportJobResponse(
        id=job_id,
        task_id=task_id,
        export_type=export_type.value,
        status="PENDING",
        sample_count=len(cmd.sample_ids),
        processed_count=0,
        skipped_count=None,
        warning_message=None,
    ))


@router.get(
    "/{task_id}/samples/export/{job_id}",
    response_model=OkResp[ExportJobResponse],
    status_code=status.HTTP_200_OK,
)
async def get_export_status(
    task_id: int,
    job_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get export job status.
    """

    job = crud_export_job.get(db=db, job_id=job_id)
    if not job:
        raise LabelUException(
            code=ErrorCode.CODE_61000_NO_DATA,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    skipped_count, warning_message = _export_progress(
        sample_count=job.sample_count,
        processed_count=job.processed_count,
        status=job.status,
    )

    return OkResp[ExportJobResponse](data=ExportJobResponse(
        id=job.id,
        task_id=job.task_id,
        export_type=job.export_type,
        status=job.status,
        sample_count=job.sample_count,
        processed_count=job.processed_count,
        skipped_count=skipped_count,
        warning_message=warning_message,
        file_path=job.file_path,
        error_message=job.error_message,
        created_at=job.created_at,
        updated_at=job.updated_at,
    ))


@router.get(
    "/{task_id}/samples/export/{job_id}/download",
    status_code=status.HTTP_200_OK,
)
async def download_export(
    task_id: int,
    job_id: int,
    authorization: HTTPAuthorizationCredentials = Security(security),
    db: Session = Depends(db_module.get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Download completed export file.
    """

    job = crud_export_job.get(db=db, job_id=job_id)
    if not job or job.status != "COMPLETED":
        raise LabelUException(
            code=ErrorCode.CODE_61000_NO_DATA,
            status_code=status.HTTP_404_NOT_FOUND,
        )

    storage = get_storage_backend()
    if storage.is_remote:
        download_url = storage.get_read_url(job.file_path)
        return RedirectResponse(url=download_url, status_code=status.HTTP_307_TEMPORARY_REDIRECT)

    file_path = Path(job.file_path)
    media_type = ".json" if file_path.suffix == ".json" else file_path.suffix.strip(".")
    return FileResponse(
        path=file_path, filename=file_path.name, media_type=f"application/{media_type}"
    )
