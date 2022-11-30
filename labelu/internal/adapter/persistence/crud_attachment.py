from typing import List

from sqlalchemy.orm import Session

from labelu.internal.domain.models.attachment import TaskAttachment


def create(db: Session, attachment: TaskAttachment) -> TaskAttachment:
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


def get(db: Session, attachment_id: int) -> TaskAttachment:
    return db.query(TaskAttachment).filter(TaskAttachment.id == attachment_id).first()


def get_by_ids(db: Session, attachment_ids: List[int]) -> List[TaskAttachment]:
    return db.query(TaskAttachment).filter(TaskAttachment.id.in_(attachment_ids)).all()


def delete(db: Session, attachment_ids: List[int]) -> None:
    db.query(TaskAttachment).filter(TaskAttachment.id.in_(attachment_ids)).delete()
    db.commit()
