from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class ExportJobResponse(BaseModel):
    id: int
    task_id: int
    export_type: str
    status: str
    sample_count: int
    processed_count: int
    skipped_count: Optional[int] = None
    warning_message: Optional[str] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
