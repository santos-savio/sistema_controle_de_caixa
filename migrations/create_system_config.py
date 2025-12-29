"""create system_config table

Revision ID: create_system_config
Revises: 
Create Date: 2025-12-29 17:48:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'create_system_config'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create system_config table
    op.create_table('system_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Text(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create unique index on key
    op.create_index(op.f('ix_system_config_key'), 'system_config', ['key'], unique=True)


def downgrade():
    # Drop system_config table
    op.drop_index(op.f('ix_system_config_key'), table_name='system_config')
    op.drop_table('system_config')
