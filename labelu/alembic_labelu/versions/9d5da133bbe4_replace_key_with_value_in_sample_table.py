"""replace key with value in sample table

Revision ID: 9d5da133bbe4
Revises: e76c2ca5562e
Create Date: 2023-03-07 10:41:33.590250

"""
import json

from alembic import op
from alembic import context
from sqlalchemy import update
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.automap import automap_base


# revision identifiers, used by Alembic.
revision = "9d5da133bbe4"
down_revision = "e76c2ca5562e"
branch_labels = None
depends_on = None

# produce a set of mappings from this MetaData
Base = automap_base()


def upgrade() -> None:
    """Replace key with value in sample table"""

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
        task_items = session.execute(
            "SELECT id, config FROM task WHERE config IS NOT NULL"
        )
        for task_item in task_items:
            label_dict = {"无标签": "noneAttribute"}
            task_id = task_item[0]
            task_config = task_item[1]
            task_config = json.loads(task_config)

            # obtain the labels in current task
            # get the general labels
            for normal_label in task_config.get("attribute", []):
                if normal_label.get("key", ""):
                    label_dict[normal_label.get("key")] = normal_label.get("value")
            # get the labels in configuration defined by user
            for task_tool in task_config.get("tools", []):
                labels = task_tool.get("config").get("attributeList", [])
                for label in labels:
                    if label.get("key", ""):
                        label_dict[label.get("key")] = label.get("value")

            # replace key with value in the sample of current task
            # get the sample data items of the task id
            sample_items = session.execute(
                f"SELECT id, data FROM task_sample WHERE task_id={task_id} AND annotated_count > 0"
            )
            # if task have several annotated sample, continute to replace key with value
            for sample_item in sample_items:
                sample_id = sample_item[0]
                sample_data_item = json.loads(sample_item[1])
                sample_annotated_result = json.loads(sample_data_item.get("result"))
                for sample_tool in sample_annotated_result.keys():
                    if sample_tool.endswith("Tool"):
                        for sample_tool_result in sample_annotated_result.get(
                            sample_tool
                        ).get("result", []):
                            tool_label = sample_tool_result.get("attribute", "")
                            if tool_label in label_dict:
                                sample_tool_result["attribute"] = label_dict[tool_label]
                sample_data_item["result"] = json.dumps(
                    sample_annotated_result, ensure_ascii=False
                )
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
