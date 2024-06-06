from datetime import datetime
import json
from typing import Any, Dict, List, Union


from sqlalchemy.orm import Session

from labelu.internal.domain.models.pre_annotation_detail import TaskPreAnnotationDetail

def create(db: Session, task_id: int, pre_annotation_id: int, sample_name: str, data: Dict[str, Any], created_by: int) -> TaskPreAnnotationDetail:
    detail = TaskPreAnnotationDetail(
        task_id=task_id,
        pre_annotation_id=pre_annotation_id,
        sample_name=sample_name,
        data=json.dumps(data),
        created_by=created_by,
    )
    db.add(detail)
    db.commit()
    db.refresh(detail)
    return detail

def list_by_task_id(db: Session,
                    task_id: int,
                    after: Union[int, None],
    before: Union[int, None],
    pageNo: Union[int, None],
    pageSize: int
) -> List[TaskPreAnnotationDetail]:
    query_filter = [TaskPreAnnotationDetail.deleted_at == None]
    
    if before:
        query_filter.append(TaskPreAnnotationDetail.id < before)
    if after:
        query_filter.append(TaskPreAnnotationDetail.id > after)
    if task_id:
        query_filter.append(TaskPreAnnotationDetail.task_id == task_id)
        
    query = db.query(TaskPreAnnotationDetail).filter(*query_filter)
    
    if before:
        query = query.order_by(TaskPreAnnotationDetail.id.desc())
    else:
        query = query.order_by(TaskPreAnnotationDetail.id.asc())
    
    results = (
        query.offset(offset=pageNo * pageSize if pageNo else 0)
        .limit(limit=pageSize)
        .all()
    )
    
    if before:
        results.reverse()
    
    return results

def list_by_task_id_and_sample_name(
    db: Session,
    task_id: int,
    sample_name: str,
) -> List[TaskPreAnnotationDetail]:
    results = db.query(TaskPreAnnotationDetail).filter(
        TaskPreAnnotationDetail.task_id == task_id,
        TaskPreAnnotationDetail.sample_name == sample_name
    ).all()
    
    return results

def delete(db: Session, detail_ids: List[int]) -> None:
    db.query(TaskPreAnnotationDetail).filter(TaskPreAnnotationDetail.id.in_(detail_ids)).update(
        {TaskPreAnnotationDetail.deleted_at: datetime.now()}
    )
    
def delete_by_pre_annotation_ids(db: Session, ids: List[int]) -> None:
    db.query(TaskPreAnnotationDetail).filter(TaskPreAnnotationDetail.task_id.in_(ids)).update(
        {TaskPreAnnotationDetail.deleted_at: datetime.now()}
    )
