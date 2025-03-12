import json

from alembic import op
import sqlalchemy as sa

def table_exist(table_name):
    """check table is not exist

    Args:
        table_name (string): the name of table

    Returns:
        bool: true or false, whether the table_name exists
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    return table_name in tables

def column_exist_in_table(table_name, column_name):
    """check column is not exist in table

    Args:
        table_name (string): the name of table
        column_name (string): the name of column

    Returns:
        bool: true or false, whether the column_name exists in the table_name
    """
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = inspector.get_columns(table_name)
    
    return column_name in [column["name"] for column in columns]


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
