"""Change Result format

Revision ID: 0145db0fec34
Revises: 363f9eea797e
Create Date: 2023-04-06 14:52:24.255060

"""
from alembic import op
from alembic import context
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base
from pydantic import BaseModel
from typing import Optional
import json

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

    def to_new(self):
        new_result = NewResult.parse_obj(self.dict())
        new_result.attributes = {self.attribute: self.textAttribute}
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