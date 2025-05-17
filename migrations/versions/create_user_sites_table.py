"""create user sites table

Revision ID: a1b2c3d4e5f6
Revises: previous_revision_id
Create Date: 2023-10-10 12:34:56.789012

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'a1b2c3d4e5f6'
down_revision = '9f843915c9ad'  # replace with actual previous revision
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('user_sites',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('resume_serial', sa.Integer(), nullable=False),
        sa.Column('subdomain', sa.String(length=100), nullable=False),
        sa.Column('html_content', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('subdomain'),
        sa.UniqueConstraint('user_id', 'resume_serial', name='uix_user_resume')
    )


def downgrade():
    op.drop_table('user_sites') 