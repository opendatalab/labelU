"""replace key with value in sample table and display unicode as the corresponding Chinese

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

def get_tool_label_dict(task_config: dict) -> dict:
    """get the key value of labels in a given task_id and task_config"""

    label_dict = {"无标签": "noneAttribute"}
    # obtain the labels in current task
    # get the general labels
    for normal_label in task_config.get("attribute", []):
        if normal_label.get("key", ""):
            label_dict[normal_label.get("key")] = normal_label.get("value")
    # get the labels in configuration defined by user
    for task_tool in task_config.get("tools", []):
        if "config" not in task_tool.keys():
            continue
        labels = task_tool.get("config").get("attributeList", [])
        for label in labels:
            if label.get("key", ""):
                label_dict[label.get("key")] = label.get("value")
    return label_dict


def replace_key_with_value(sample_data: dict, label_dict: dict) -> dict:
    """replace the key with value in task_sample table to modify the error for the history version"""

    annotated_result = sample_data.get("result")
    annotated_result = json.loads(annotated_result)
    for sample_tool, sample_tool_results in annotated_result.items():
        if sample_tool.endswith("Tool"):
            for sample_tool_result in sample_tool_results.get("result", []):
                tool_label = sample_tool_result.get("attribute", "")
                if tool_label in label_dict:
                    sample_tool_result["attribute"] = label_dict[tool_label]
    return annotated_result

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
            'SELECT id, config FROM task WHERE config IS NOT NULL AND config != ""'
        )
        for task_item in task_items:
            task_id = task_item[0]
            task_config = json.loads(task_item[1])
            label_dict = get_tool_label_dict(task_config)
            # replace key with value in the sample of current task
            # get the sample data items of the task id
            sample_items = session.execute(
                f"SELECT id, data, annotated_count FROM task_sample WHERE task_id={task_id}"
            )
            # if task have several annotated sample, continute to replace key with value
            for sample_item in sample_items:
                sample_id = sample_item[0]
                sample_data_item = json.loads(sample_item[1])
                # replace key with value and display unicode as the corresponding Chinesedisplays unicode as the corresponding Chinese
                if sample_item[2] > 0:
                    sample_annotated_result = replace_key_with_value(
                        sample_data_item, label_dict
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
