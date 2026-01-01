"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-12-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import geoalchemy2
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create ENUM types
    sex_enum = postgresql.ENUM('male', 'female', 'unknown', name='sex_enum')
    sex_enum.create(op.get_bind(), checkfirst=True)

    size_enum = postgresql.ENUM('small', 'medium', 'large', name='size_enum')
    size_enum.create(op.get_bind(), checkfirst=True)

    animal_enum = postgresql.ENUM('dog', 'cat', 'other', name='animal_enum')
    animal_enum.create(op.get_bind(), checkfirst=True)

    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
    )
    op.create_index('ix_users_id', 'users', ['id'])
    op.create_index('ix_users_email', 'users', ['email'])

    # Create posts table
    op.create_table(
        'posts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('image_url', sa.String(500), nullable=False),
        sa.Column('thumbnail_url', sa.String(500), nullable=False),
        sa.Column('sex', sex_enum, nullable=False, server_default='unknown'),
        sa.Column('size', size_enum, nullable=False),
        sa.Column('animal_type', animal_enum, nullable=False, server_default='dog'),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', geoalchemy2.Geography(geometry_type='POINT', srid=4326), nullable=False),
        sa.Column('location_name', sa.String(200), nullable=True),
        sa.Column('sighting_date', sa.Date(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('contact_method', sa.String(200), nullable=True),
        sa.Column('embedding', Vector(512), nullable=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.CheckConstraint('char_length(description) <= 1000', name='description_length_check'),
        # Foreign key will be added when auth is implemented
        # sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
    )

    # Create indexes for posts
    op.create_index('ix_posts_id', 'posts', ['id'])
    op.create_index('ix_posts_sex', 'posts', ['sex'])
    op.create_index('ix_posts_size', 'posts', ['size'])
    op.create_index('ix_posts_animal_type', 'posts', ['animal_type'])
    op.create_index('ix_posts_sighting_date', 'posts', ['sighting_date'], postgresql_ops={'sighting_date': 'DESC'})
    op.create_index('ix_posts_created_at', 'posts', ['created_at'], postgresql_ops={'created_at': 'DESC'})
    op.create_index('ix_posts_is_active', 'posts', ['is_active'], postgresql_where=sa.text('is_active = true'))

    # Create spatial index for location
    op.execute('CREATE INDEX idx_posts_location ON posts USING GIST (location);')

    # Create vector index for embeddings (HNSW)
    op.execute('''
        CREATE INDEX idx_posts_embedding ON posts
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64);
    ''')


def downgrade() -> None:
    # Drop indexes
    op.execute('DROP INDEX IF EXISTS idx_posts_embedding;')
    op.execute('DROP INDEX IF EXISTS idx_posts_location;')
    op.drop_index('ix_posts_is_active', 'posts')
    op.drop_index('ix_posts_created_at', 'posts')
    op.drop_index('ix_posts_sighting_date', 'posts')
    op.drop_index('ix_posts_animal_type', 'posts')
    op.drop_index('ix_posts_size', 'posts')
    op.drop_index('ix_posts_sex', 'posts')
    op.drop_index('ix_posts_id', 'posts')

    # Drop tables
    op.drop_table('posts')

    op.drop_index('ix_users_email', 'users')
    op.drop_index('ix_users_id', 'users')
    op.drop_table('users')

    # Drop ENUMs
    animal_enum = postgresql.ENUM('dog', 'cat', 'other', name='animal_enum')
    animal_enum.drop(op.get_bind(), checkfirst=True)

    size_enum = postgresql.ENUM('small', 'medium', 'large', name='size_enum')
    size_enum.drop(op.get_bind(), checkfirst=True)

    sex_enum = postgresql.ENUM('male', 'female', 'unknown', name='sex_enum')
    sex_enum.drop(op.get_bind(), checkfirst=True)
