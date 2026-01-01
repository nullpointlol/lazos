"""add_alerts_table

Revision ID: bd61a4fb8a8b
Revises: 001
Create Date: 2025-12-26 13:59:04.591445

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
from geoalchemy2 import Geography


# revision identifiers, used by Alembic.
revision = 'bd61a4fb8a8b'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create alerts table
    op.create_table(
        'alerts',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('animal_type', sa.Enum('dog', 'cat', 'other', name='animal_type_enum'), nullable=False),
        sa.Column('direction', sa.String(200), nullable=True),
        sa.Column('location', Geography('POINT', srid=4326), nullable=False),
        sa.Column('location_name', sa.String(200), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
    )

    # Create spatial index on location
    op.execute("""
        CREATE INDEX idx_alerts_location
        ON alerts
        USING GIST (location);
    """)

    # Create index on created_at for sorting
    op.create_index('idx_alerts_created_at', 'alerts', ['created_at'], postgresql_using='btree')

    # Create index on animal_type for filtering
    op.create_index('idx_alerts_animal_type', 'alerts', ['animal_type'], postgresql_using='btree')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_alerts_animal_type', table_name='alerts')
    op.drop_index('idx_alerts_created_at', table_name='alerts')
    op.execute("DROP INDEX IF EXISTS idx_alerts_location;")

    # Drop table
    op.drop_table('alerts')
