"""Create portal submissions table

Revision ID: 6b415e63cdaa
Revises: 6bbff1fcdc1b
Create Date: 2025-09-30 16:34:41.918126

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6b415e63cdaa'
down_revision: Union[str, Sequence[str], None] = '6bbff1fcdc1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create portal_submissions table
    op.create_table(
        'portal_submissions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('client_id', sa.Integer(), nullable=True),
        sa.Column('project_requirements', sa.Text(), nullable=False),
        sa.Column('budget_range', sa.String(), nullable=False),
        sa.Column('timeline', sa.String(), nullable=False),
        sa.Column('additional_info', sa.Text(), nullable=True),
        sa.Column('preferred_contact_method', sa.String(), nullable=True),
        sa.Column('urgency_level', sa.String(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['client_id'], ['clients.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Downgrade schema."""
    # Drop portal_submissions table
    op.drop_table('portal_submissions')
