"""add_cover_letters_table

Revision ID: 7ae077e9d602
Revises: e40c1986d78e
Create Date: 2026-03-04 15:03:01.295509

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7ae077e9d602'
down_revision: Union[str, Sequence[str], None] = 'e40c1986d78e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'cover_letters',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('job_id', sa.UUID(), nullable=False),
        sa.Column('resume_id', sa.UUID(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('tone', sa.Enum('professional', 'enthusiastic', 'creative', 'formal', name='coverlettertone'), nullable=True),
        sa.Column('word_count', sa.String(length=50), nullable=True),
        sa.Column('is_favorite', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['job_id'], ['jobs.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['resume_id'], ['resumes.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cover_letters_user_id'), 'cover_letters', ['user_id'], unique=False)
    op.create_index(op.f('ix_cover_letters_job_id'), 'cover_letters', ['job_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_cover_letters_job_id'), table_name='cover_letters')
    op.drop_index(op.f('ix_cover_letters_user_id'), table_name='cover_letters')
    op.drop_table('cover_letters')
    op.execute('DROP TYPE coverlettertone')
