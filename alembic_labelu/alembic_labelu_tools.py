from alembic import op
from sqlalchemy import engine_from_config
from sqlalchemy.engine import reflection


def column_exist_in_table(table_name, column_name):
    """check column is not exist in table

    Args:
        table_name (string): the name of table
        column_name (string): the name of column

    Returns:
        bool: true or false, whether the column_name exists in the table_name
    """
    config = op.get_context().config
    engine = engine_from_config(
        config.get_section(config.config_ini_section), prefix="sqlalchemy."
    )
    insp = reflection.Inspector.from_engine(engine)
    column_exist = False
    for col in insp.get_columns(table_name):
        if column_name not in col["name"]:
            continue
        column_exist = True
    return column_exist
