from typing import Any, Dict

from sqlalchemy.orm import Session
from fastapi.encoders import jsonable_encoder

from labelu.internal.domain.models.sample_max_id import TaskSampleMaxId


def create(db:Session, sample_max_id_item: TaskSampleMaxId) -> TaskSampleMaxId:
    db.add(sample_max_id_item)
    db.flush()
    db.refresh(sample_max_id_item)
    return sample_max_id_item

def get(db:Session, task_id: int) -> TaskSampleMaxId:
    return(
        db.query(TaskSampleMaxId)
        .filter(TaskSampleMaxId.task_id==task_id)
        .first()
    )

def update(db:Session, db_obj: TaskSampleMaxId, obj_in: Dict[str, Any]) -> TaskSampleMaxId:
    obj_data = jsonable_encoder(obj_in)
    for field in obj_data:
        if field in obj_in:
            setattr(db_obj, field, obj_in[field])
    db.add(db_obj)
    db.flush()
    db.refresh(db_obj)
    return db_obj