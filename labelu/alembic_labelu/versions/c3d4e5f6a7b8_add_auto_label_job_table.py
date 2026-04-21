"""add auto_label_job table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-20 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c3d4e5f6a7b8'
down_revision = 'b2c3d4e5f6a7'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'auto_label_job' not in tables:
        op.create_table(
            'auto_label_job',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('task_id', sa.Integer(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=True),
            sa.Column('status', sa.String(length=32), nullable=True),
            sa.Column('sample_count', sa.Integer(), nullable=True),
            sa.Column('processed_count', sa.Integer(), nullable=True),
            sa.Column('success_count', sa.Integer(), nullable=True),
            sa.Column('failed_count', sa.Integer(), nullable=True),
            sa.Column('filter_by_labels', sa.Boolean(), nullable=True),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['task_id'], ['task.id']),
            sa.ForeignKeyConstraint(['created_by'], ['user.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_auto_label_job_id', 'auto_label_job', ['id'])
        op.create_index('ix_auto_label_job_task_id', 'auto_label_job', ['task_id'])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'auto_label_job' in tables:
        op.drop_index('ix_auto_label_job_task_id', table_name='auto_label_job')
        op.drop_index('ix_auto_label_job_id', table_name='auto_label_job')
        op.drop_table('auto_label_job')
