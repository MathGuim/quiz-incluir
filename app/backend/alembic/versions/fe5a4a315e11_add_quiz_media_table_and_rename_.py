"""add quiz_media table and rename vocabulary category

Revision ID: fe5a4a315e11
Revises: 9363763904ae
Create Date: 2026-08-08 15:08:52.637241

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = 'fe5a4a315e11'
down_revision: Union[str, Sequence[str], None] = '9363763904ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('quiz_media',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('quiz_id', sa.Uuid(), nullable=False),
    sa.Column('type', sa.Enum('TEXT', 'IMAGE', 'AUDIO', 'VIDEO', name='mediatype', create_type=False), nullable=False),
    sa.Column('url', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('caption', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
    sa.Column('position', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['quiz_id'], ['quizzes.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_quiz_media_quiz_id'), 'quiz_media', ['quiz_id'], unique=False)

    op.execute("ALTER TYPE quizcategory RENAME VALUE 'VOCABULARY' TO 'VOCABULARY_GRAMMAR'")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("ALTER TYPE quizcategory RENAME VALUE 'VOCABULARY_GRAMMAR' TO 'VOCABULARY'")

    op.drop_index(op.f('ix_quiz_media_quiz_id'), table_name='quiz_media')
    op.drop_table('quiz_media')
