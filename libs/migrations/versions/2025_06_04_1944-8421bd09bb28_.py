"""

Revision ID: 8421bd09bb28
Revises: 196d5caccf85
Create Date: 2025-06-04 19:44:13.161393

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "8421bd09bb28"
down_revision = "196d5caccf85"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "chat_messages",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("is_user", sa.Boolean(), nullable=False),
        sa.Column("timestamp", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.drop_table("celery_tasksetmeta")
    op.drop_table("celery_taskmeta")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "celery_taskmeta",
        sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("task_id", sa.VARCHAR(length=155), autoincrement=False, nullable=True),
        sa.Column("status", sa.VARCHAR(length=50), autoincrement=False, nullable=True),
        sa.Column("result", postgresql.BYTEA(), autoincrement=False, nullable=True),
        sa.Column("date_done", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.Column("traceback", sa.TEXT(), autoincrement=False, nullable=True),
        sa.Column("name", sa.VARCHAR(length=155), autoincrement=False, nullable=True),
        sa.Column("args", postgresql.BYTEA(), autoincrement=False, nullable=True),
        sa.Column("kwargs", postgresql.BYTEA(), autoincrement=False, nullable=True),
        sa.Column("worker", sa.VARCHAR(length=155), autoincrement=False, nullable=True),
        sa.Column("retries", sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column("queue", sa.VARCHAR(length=155), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("celery_taskmeta_pkey")),
        sa.UniqueConstraint(
            "task_id",
            name=op.f("celery_taskmeta_task_id_key"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.create_table(
        "celery_tasksetmeta",
        sa.Column("id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("taskset_id", sa.VARCHAR(length=155), autoincrement=False, nullable=True),
        sa.Column("result", postgresql.BYTEA(), autoincrement=False, nullable=True),
        sa.Column("date_done", postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("celery_tasksetmeta_pkey")),
        sa.UniqueConstraint(
            "taskset_id",
            name=op.f("celery_tasksetmeta_taskset_id_key"),
            postgresql_include=[],
            postgresql_nulls_not_distinct=False,
        ),
    )
    op.drop_table("chat_messages")
    # ### end Alembic commands ###
