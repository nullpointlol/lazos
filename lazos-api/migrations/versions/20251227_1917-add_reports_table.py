"""add reports table

Revision ID: 20251227_1917
Revises: bd61a4fb8a8b
Create Date: 2025-12-27 19:17:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20251227_1917'
down_revision = 'bd61a4fb8a8b'
branch_labels = None
depends_on = None


def upgrade():
    # Create enum for report reasons
    op.execute("CREATE TYPE report_reason_enum AS ENUM ('not_animal', 'inappropriate', 'spam', 'other')")

    # Create reports table
    op.create_table('reports',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('post_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('reason', postgresql.ENUM('not_animal', 'inappropriate', 'spam', 'other', name='report_reason_enum'), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('reporter_ip', sa.String(length=45), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('resolved', sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reports_id'), 'reports', ['id'], unique=False)
    op.create_index(op.f('ix_reports_post_id'), 'reports', ['post_id'], unique=False)
    op.create_index(op.f('ix_reports_reason'), 'reports', ['reason'], unique=False)
    op.create_index(op.f('ix_reports_created_at'), 'reports', ['created_at'], unique=False)
    op.create_index(op.f('ix_reports_resolved'), 'reports', ['resolved'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_reports_resolved'), table_name='reports')
    op.drop_index(op.f('ix_reports_created_at'), table_name='reports')
    op.drop_index(op.f('ix_reports_reason'), table_name='reports')
    op.drop_index(op.f('ix_reports_post_id'), table_name='reports')
    op.drop_index(op.f('ix_reports_id'), table_name='reports')
    op.drop_table('reports')
    op.execute("DROP TYPE report_reason_enum")
