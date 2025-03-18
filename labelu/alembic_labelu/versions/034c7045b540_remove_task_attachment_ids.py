"""remove_task_attachment_ids

Revision ID: 034c7045b540
Revises: 2eb983c9a254
Create Date: 2025-03-13 22:43:30.564428

"""
from alembic import op

from labelu.alembic_labelu.alembic_labelu_tools import column_exist_in_table

# revision identifiers, used by Alembic.
revision = '034c7045b540'
down_revision = '2eb983c9a254'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # remove task_attachment_ids column from task sample table
    # fix the unnecessary column from: https://github.com/opendatalab/labelU/blob/v1.2.1/labelu/alembic_labelu/versions/2eb983c9a254_add_collaborators_and_updaters.py#L143
    if column_exist_in_table('task_sample', 'task_attachment_ids'):
        op.drop_column('task_sample', 'task_attachment_ids')


def downgrade() -> None:
    if not column_exist_in_table('task_sample', 'task_attachment_ids'):
        op.execute('ALTER TABLE task_sample ADD COLUMN task_attachment_ids TEXT COMMENT "task attachment ids"')
