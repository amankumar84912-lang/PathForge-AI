"""Add categories to career goals."""
from alembic import op
import sqlalchemy as sa

revision = "0003_career_categories"
down_revision = "0002_task_skip"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "careers",
        sa.Column("category", sa.String(length=80), nullable=False, server_default="Software Development"),
    )


def downgrade() -> None:
    op.drop_column("careers", "category")
