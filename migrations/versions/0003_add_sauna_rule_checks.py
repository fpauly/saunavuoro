"""add checks for sauna booking rules

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-19
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_saunas_turn_length", "saunas", "turn_length_minutes > 0"
    )
    op.create_check_constraint(
        "ck_saunas_max_extra_bookings", "saunas", "max_extra_bookings_per_week >= 0"
    )
    op.create_check_constraint(
        "ck_saunas_max_days_ahead", "saunas", "max_days_ahead >= 0"
    )
    op.create_check_constraint(
        "ck_saunas_cancellation_deadline", "saunas", "cancellation_deadline_hours >= 0"
    )


def downgrade() -> None:
    op.drop_constraint("ck_saunas_cancellation_deadline", "saunas", type_="check")
    op.drop_constraint("ck_saunas_max_days_ahead", "saunas", type_="check")
    op.drop_constraint("ck_saunas_max_extra_bookings", "saunas", type_="check")
    op.drop_constraint("ck_saunas_turn_length", "saunas", type_="check")
