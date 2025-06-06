"""

Revision ID: 196d5caccf85
Revises:
Create Date: 2025-06-03 21:44:26.614886

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "196d5caccf85"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "users",
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=True),
        sa.Column("is_verified", sa.Boolean(), nullable=True),
        sa.Column("role", sa.String(length=50), nullable=True),
        sa.Column("first_name", sa.String(length=100), nullable=True),
        sa.Column("last_name", sa.String(length=100), nullable=True),
        sa.Column("date_of_birth", sa.DateTime(), nullable=True),
        sa.Column("profile_picture", sa.String(length=255), nullable=True),
        sa.Column("gender", sa.String(length=10), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("weight", sa.Integer(), nullable=True),
        sa.Column("bmi", sa.Integer(), nullable=True),
        sa.Column("body_tracker_period", sa.String(length=20), nullable=True),
        sa.Column("language", sa.String(length=10), nullable=True),
        sa.Column("referral_code", sa.String(length=50), nullable=True),
        sa.Column("country", sa.String(length=100), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=True),
        sa.Column("address", sa.String(length=255), nullable=True),
        sa.Column("phone_number", sa.String(length=20), nullable=True),
        sa.Column("timezone", sa.String(length=100), nullable=True),
        sa.Column("preferences", sa.JSON(), nullable=True),
        sa.Column("last_login", sa.DateTime(), nullable=True),
        sa.Column("reset_token", sa.String(length=255), nullable=True),
        sa.Column("reset_token_expiry", sa.DateTime(), nullable=True),
        sa.Column("package_type", sa.String(length=50), nullable=True),
        sa.Column("subscription_start", sa.DateTime(), nullable=True),
        sa.Column("subscription_end", sa.DateTime(), nullable=True),
        sa.Column("billing_period", sa.String(length=20), nullable=True),
        sa.Column("auto_renew", sa.Boolean(), nullable=True),
        sa.Column("usage_limit", sa.Integer(), nullable=True),
        sa.Column("storage_limit", sa.Integer(), nullable=True),
        sa.Column("package_features", sa.JSON(), nullable=True),
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_date", sa.DateTime(), server_default=sa.text("now()"), nullable=True),
        sa.Column("updated_date", sa.DateTime(), nullable=True),
        sa.Column("deleted_date", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
    # ### end Alembic commands ###
