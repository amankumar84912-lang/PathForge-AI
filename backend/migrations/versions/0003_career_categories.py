"""Add categories to career goals."""
from alembic import op
import sqlalchemy as sa

revision = "0003_career_categories"
down_revision = "0002_task_skip"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # The initial migration creates tables from the current ORM metadata.
    # On a fresh database that metadata already includes this column, so
    # avoid issuing a duplicate ALTER TABLE in that case.
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("careers") and "category" not in {
        column["name"] for column in inspector.get_columns("careers")
    }:
        op.add_column(
            "careers",
            sa.Column("category", sa.String(length=80), nullable=False, server_default="Software Development"),
        )


def downgrade() -> None:
    inspector = sa.inspect(op.get_bind())
    if inspector.has_table("careers") and "category" in {
        column["name"] for column in inspector.get_columns("careers")
    }:
        op.drop_column("careers", "category")
