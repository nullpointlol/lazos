"""add moderation fields to posts

Revision ID: 20251231_0000
Revises: 20251228_0000
Create Date: 2025-12-31 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251231_0000'
down_revision = '20251228_0000'
branch_labels = None
depends_on = None


def upgrade():
    # Add pending_approval column with default False
    op.add_column('posts',
        sa.Column('pending_approval', sa.Boolean(), nullable=False, server_default='false')
    )

    # Add moderation_reason column (nullable)
    op.add_column('posts',
        sa.Column('moderation_reason', sa.String(length=500), nullable=True)
    )

    # Add moderation_date column (nullable)
    op.add_column('posts',
        sa.Column('moderation_date', sa.DateTime(timezone=True), nullable=True)
    )

    # Create index on pending_approval for faster queries
    op.create_index('ix_posts_pending_approval', 'posts', ['pending_approval'], unique=False)

    # Create composite index for active and approved posts (most common query)
    op.create_index(
        'ix_posts_active_approved',
        'posts',
        ['is_active', 'pending_approval'],
        unique=False,
        postgresql_where=sa.text('is_active = true AND pending_approval = false')
    )


def downgrade():
    # Drop indexes
    op.drop_index('ix_posts_active_approved', table_name='posts')
    op.drop_index('ix_posts_pending_approval', table_name='posts')

    # Drop columns
    op.drop_column('posts', 'moderation_date')
    op.drop_column('posts', 'moderation_reason')
    op.drop_column('posts', 'pending_approval')
