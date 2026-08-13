"""add quizzes.category and quizzes.level

The initial schema revision (9363763904ae) created ``quizzes`` without the
``category`` and ``level`` columns that ``models.Quiz`` declares, and no later
revision added them. Databases built by ``SQLModel.create_all`` have the
columns; databases built by the migration chain do not, so every query against
``quizzes`` failed with UndefinedColumnError on a migration-built database.

Additive and idempotent in both directions so it is safe against either
lineage: the enum type is created only when absent, and the columns use
ADD COLUMN IF NOT EXISTS.

Revision ID: a1c4e7d9b2f0
Revises: fe5a4a315e11
"""
from typing import Sequence, Union

from alembic import op

revision: str = 'a1c4e7d9b2f0'
down_revision: Union[str, Sequence[str], None] = 'fe5a4a315e11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'quizcategory') THEN
                CREATE TYPE quizcategory AS ENUM ('READING', 'LISTENING', 'VOCABULARY_GRAMMAR');
            END IF;
        END $$;
        """
    )
    op.execute(
        "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS category quizcategory "
        "NOT NULL DEFAULT 'READING'"
    )
    op.execute(
        "ALTER TABLE quizzes ADD COLUMN IF NOT EXISTS level languagelevel "
        "NOT NULL DEFAULT 'A1'"
    )


def downgrade() -> None:
    op.execute("ALTER TABLE quizzes DROP COLUMN IF EXISTS level")
    op.execute("ALTER TABLE quizzes DROP COLUMN IF EXISTS category")
