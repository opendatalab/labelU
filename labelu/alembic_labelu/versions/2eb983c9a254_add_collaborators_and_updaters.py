"""add_collaborators_and_updaters

Revision ID: 2eb983c9a254
Revises: eb9c5b98168b
Create Date: 2025-02-19 16:16:39.259779

"""
from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column

# revision identifiers, used by Alembic.
revision = '2eb983c9a254'
down_revision = 'eb9c5b98168b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create task_collaborator table
    # if the table is not exists then create it
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'task_collaborator' not in tables:
        op.create_table(
            'task_collaborator',
            sa.Column('task_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column(
                'created_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('CURRENT_TIMESTAMP'),
                nullable=False
            ),
            sa.ForeignKeyConstraint(
                ['task_id'],
                ['task.id'],
                ondelete='CASCADE'
            ),
            sa.ForeignKeyConstraint(
                ['user_id'],
                ['user.id'],
                ondelete='CASCADE'
            ),
            sa.PrimaryKeyConstraint('task_id', 'user_id')
        )
        
        # Performances index
        indices = inspector.get_indexes('task_collaborator')
        existing_index_names = {idx['name'] for idx in indices}
        
        if 'ix_task_collaborator_task_id' not in existing_index_names:
            op.create_index(
                'ix_task_collaborator_task_id',
                'task_collaborator',
                ['task_id']
            )
            op.create_index(
                'ix_task_collaborator_user_id',
                'task_collaborator',
                ['user_id']
            )
            op.create_index(
                'ix_task_created_by_deleted_at',
                'task',
                ['created_by', 'deleted_at']
            )
    
    # Task sample: updater -> updaters; create a new table task_sample_updater
    if 'task_sample_updater' not in tables:
        op.create_table(
            'task_sample_updater',
            sa.Column('sample_id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column(
                'created_at',
                sa.DateTime(timezone=True),
                server_default=sa.text('CURRENT_TIMESTAMP'),
                nullable=False
            ),
            sa.ForeignKeyConstraint(
                ['sample_id'],
                ['task_sample.id'],
                ondelete='CASCADE'
            ),
            sa.ForeignKeyConstraint(
                ['user_id'],
                ['user.id'],
                ondelete='CASCADE'
            ),
            sa.PrimaryKeyConstraint('sample_id', 'user_id')
        )
        
        # Performances index
        # check if the index is already exists
        indices = inspector.get_indexes('task_sample_updater')
        existing_index_names = {idx['name'] for idx in indices}
        
        if 'ix_task_sample_updater_sample_id' not in existing_index_names:
            op.create_index(
                'ix_task_sample_updater_sample_id',
                'task_sample_updater',
                ['sample_id']
            )
            op.create_index(
                'ix_task_sample_updater_user_id',
                'task_sample_updater',
                ['user_id']
            )
    
     # Migrate data from task_sample.updated_by to task_sample_updater
    task_sample = table(
        'task_sample',
        column('id', sa.Integer),
        column('updated_by', sa.Integer),
        column('updated_at', sa.DateTime)
    )
    
    task_sample_updater = table(
        'task_sample_updater',
        column('sample_id', sa.Integer),
        column('user_id', sa.Integer),
        column('created_at', sa.DateTime)
    )
    
    conn = op.get_bind()
    for row in conn.execute(sa.select([task_sample.c.id, task_sample.c.updated_by, task_sample.c.updated_at])):
        if row.updated_by:
            conn.execute(
                task_sample_updater.insert().values(
                    sample_id=row.id,
                    user_id=row.updated_by,
                    created_at=row.updated_at or datetime.now()
                )
            )

def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()
    
    if 'task_collaborator' in tables:
        indices = inspector.get_indexes('task_collaborator')
        existing_index_names = {idx['name'] for idx in indices}
        
        if 'ix_task_collaborator_user_id' in existing_index_names:
            op.drop_index('ix_task_collaborator_user_id', table_name='task_collaborator')
        if 'ix_task_collaborator_task_id' in existing_index_names:
            op.drop_index('ix_task_collaborator_task_id', table_name='task_collaborator')
            
        op.drop_table('task_collaborator')
    
    if 'task' in tables:
        indices = inspector.get_indexes('task')
        existing_index_names = {idx['name'] for idx in indices}
        
        if 'ix_task_created_by_deleted_at' in existing_index_names:
            op.drop_index('ix_task_created_by_deleted_at', table_name='task')
    
    if 'task_sample_updater' in tables:
        indices = inspector.get_indexes('task_sample_updater')
        existing_index_names = {idx['name'] for idx in indices}
        
        if 'ix_task_sample_updater_user_id' in existing_index_names:
            op.drop_index('ix_task_sample_updater_user_id', table_name='task_sample_updater')
        if 'ix_task_sample_updater_sample_id' in existing_index_names:
            op.drop_index('ix_task_sample_updater_sample_id', table_name='task_sample_updater')
            
        op.drop_table('task_sample_updater')
