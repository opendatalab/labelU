"""add export_job table

Revision ID: a1b2c3d4e5f6
Revises: 2eb983c9a254
Create Date: 2026-03-19 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '2eb983c9a254'
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'export_job' not in tables:
        op.create_table(
            'export_job',
            sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('task_id', sa.Integer(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=True),
            sa.Column('export_type', sa.String(length=32), nullable=True),
            sa.Column('status', sa.String(length=32), nullable=True),
            sa.Column('sample_count', sa.Integer(), nullable=True),
            sa.Column('processed_count', sa.Integer(), nullable=True),
            sa.Column('file_path', sa.Text(), nullable=True),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('sample_ids', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(['task_id'], ['task.id']),
            sa.ForeignKeyConstraint(['created_by'], ['user.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('ix_export_job_id', 'export_job', ['id'])
        op.create_index('ix_export_job_task_id', 'export_job', ['task_id'])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if 'export_job' in tables:
        op.drop_index('ix_export_job_task_id', table_name='export_job')
        op.drop_index('ix_export_job_id', table_name='export_job')
        op.drop_table('export_job')
