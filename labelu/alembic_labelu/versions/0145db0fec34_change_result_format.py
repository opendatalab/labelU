"""Change Result format

Revision ID: 0145db0fec34
Revises: 363f9eea797e
Create Date: 2023-04-06 14:52:24.255060

"""
import json
from typing import Optional

from alembic import context, op
from pydantic import BaseModel
from sqlalchemy import update
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

# revision identifiers, used by Alembic.
revision = "0145db0fec34"
down_revision = "363f9eea797e"
branch_labels = None
depends_on = None

# produce a set of mappings from this MetaData
Base = automap_base()

# define the new result model
class NewResult(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    attribute: Optional[str] = None
    valid: Optional[bool] = None
    isVisible: Optional[bool] = None
    id: Optional[str] = None
    sourceID: Optional[str] = None
    textAttribute: Optional[str] = None
    order: Optional[int] = None
    attributes: Optional[dict] = None
    pointList: Optional[list] = None
    label: Optional[str] = None
    isReference: Optional[bool] = None
    disableDelete: Optional[bool] = None
    isRect: Optional[bool] = None


# define the old result model
class OldResult(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    attribute: Optional[str] = None
    valid: Optional[bool] = None
    isVisible: Optional[bool] = None
    id: Optional[str] = None
    sourceID: Optional[str] = None
    textAttribute: Optional[str] = None
    order: Optional[int] = None
    result: Optional[dict] = None
    pointList: Optional[list] = None
    label: Optional[str] = None
    isReference: Optional[bool] = None
    disableDelete: Optional[bool] = None
    isRect: Optional[bool] = None

    def to_new(self):
        new_result = NewResult(
            x=self.x,
            y=self.y,
            width=self.width,
            height=self.height,
            attribute=self.attribute,
            valid=self.valid,
            isVisible=self.isVisible,
            id=self.id,
            sourceID=self.sourceID,
            textAttribute=self.textAttribute,
            order=self.order,
            pointList=self.pointList,
            label=self.label,
            isReference=self.isReference,
            disableDelete=self.disableDelete,
            isRect=self.isRect,
        )
        new_result.attributes = (
            self.result if self.result else {self.attribute: self.textAttribute}
        )
        return new_result


def upgrade() -> None:

    # get the current connection
    bind = op.get_bind()
    # Reflect ORM models from the database
    Base.prepare(autoload_with=bind, reflect=True)
    task_sample = Base.classes.task_sample
    # make a session
    Session = sessionmaker(bind=bind)
    session = Session()

    # replace the key with value in a transaction
    with context.begin_transaction():
        sample_items = session.execute(
            'SELECT id, data FROM task_sample WHERE data IS NOT NULL AND data != ""'
        )

        for sample_item in sample_items:

            sample_id = sample_item[0]
            sample_data = json.loads(sample_item[1])
            data_result = json.loads(sample_data.get("result", ""))
            for key in data_result.keys():
                if key.endswith("Tool"):
                    data_result[key]["result"] = [
                        OldResult.parse_obj(result).to_new().dict(exclude_none=True)
                        for result in data_result[key]["result"]
                    ]

            sample_data["result"] = json.dumps(data_result, ensure_ascii=False)
            data = json.dumps(sample_data, ensure_ascii=False)

            session.execute(
                update(task_sample).where(task_sample.id == sample_id).values(data=data)
            )


def downgrade() -> None:
    pass
