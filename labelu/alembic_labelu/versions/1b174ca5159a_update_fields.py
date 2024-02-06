"""update pointList => points

Revision ID: 1b174ca5159a
Revises: 0145db0fec34
Create Date: 2024-02-01 19:26:24.048019

"""
import json
from alembic import context, op
from sqlalchemy import update
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import sessionmaker

Base = automap_base()

def update_fields(sample_data: dict) -> dict:
    """update the field pointList to points in sample_data"""
    # get the result of sample_data
    annotated_result = sample_data.get("result")
    annotated_result = json.loads(annotated_result)
    # update the field pointList to points
    for sample_tool, sample_tool_results in annotated_result.items():
        if sample_tool.endswith("Tool") and isinstance(sample_tool_results, dict):
            for sample_tool_result in sample_tool_results.get("result", []):
                keys = sample_tool_result.keys()
                # replace pointList to points
                if "pointList" in keys:
                    sample_tool_result["points"] = sample_tool_result.pop("pointList")
                # replace attribute to label
                if "attribute" in keys:
                    sample_tool_result["label"] = sample_tool_result.pop("attribute")
    return annotated_result


# revision identifiers, used by Alembic.
revision = '1b174ca5159a'
down_revision = '0145db0fec34'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Replace pointList with points in result table"""
    # get the current connection
    bind = op.get_bind()
    # Reflect ORM models from the database
    Base.prepare(autoload_with=bind, reflect=True)
    task_sample = Base.classes.task_sample
    # make a session
    Session = sessionmaker(bind=bind)
    session = Session()

    with context.begin_transaction():
        task_items = session.execute(
            'SELECT id, config FROM task WHERE config IS NOT NULL AND config != ""'
        )

        for task_item in task_items:
            task_id = task_item[0]
            
            sample_items = session.execute(
                f"SELECT id, data, annotated_count FROM task_sample WHERE task_id={task_id}"
            )
            
            for sample_item in sample_items:
                sample_id = sample_item[0]
                sample_data_item = json.loads(sample_item[1])
                if sample_item[2] > 0:
                    sample_annotated_result = update_fields(
                        sample_data_item
                    )
                    sample_data_item["result"] = json.dumps(
                        sample_annotated_result, ensure_ascii=False
                    )
                # display unicode as the corresponding Chinese
                else:
                    pass
                sample_annotated_item_str = json.dumps(
                    sample_data_item, ensure_ascii=False
                )
                op.execute(
                    update(task_sample)
                    .where(task_sample.id == sample_id)
                    .values({task_sample.data: sample_annotated_item_str})
                )

def downgrade() -> None:
    pass
