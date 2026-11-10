"""Allow learners to skip roadmap tasks."""
from alembic import op

revision = "0002_task_skip"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("task_progress") as batch:
        batch.drop_constraint("ck_task_status", type_="check")
        batch.create_check_constraint(
            "ck_task_status",
            "status IN ('not_started','in_progress','completed','skipped')",
        )


def downgrade() -> None:
    with op.batch_alter_table("task_progress") as batch:
        batch.drop_constraint("ck_task_status", type_="check")
        batch.create_check_constraint(
            "ck_task_status",
            "status IN ('not_started','in_progress','completed')",
        )
