"""create residents, saunas, weekly_turns and bookings tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-11-10
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "residents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "apartment_id",
            sa.Uuid(),
            sa.ForeignKey("apartments.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("name", sa.String(100), nullable=False),
    )
    op.create_table(
        "saunas",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("opens_at", sa.Time(), nullable=False),
        sa.Column("closes_at", sa.Time(), nullable=False),
        sa.Column("turn_length_minutes", sa.Integer(), nullable=False),
        sa.Column("max_extra_bookings_per_week", sa.Integer(), nullable=False),
        sa.Column("max_days_ahead", sa.Integer(), nullable=False),
        sa.Column("cancellation_deadline_hours", sa.Integer(), nullable=False),
        sa.CheckConstraint("closes_at > opens_at", name="ck_saunas_opening_hours"),
    )
    op.create_table(
        "weekly_turns",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "sauna_id",
            sa.Uuid(),
            sa.ForeignKey("saunas.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "apartment_id",
            sa.Uuid(),
            sa.ForeignKey("apartments.id", ondelete="RESTRICT"),
            nullable=False,
            unique=True,
        ),
        sa.Column("weekday", sa.SmallInteger(), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.UniqueConstraint("sauna_id", "weekday", "start_time", name="uq_weekly_turns_slot"),
        sa.CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_weekly_turns_weekday"),
    )
    op.create_table(
        "bookings",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "sauna_id",
            sa.Uuid(),
            sa.ForeignKey("saunas.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column(
            "apartment_id",
            sa.Uuid(),
            sa.ForeignKey("apartments.id", ondelete="RESTRICT"),
            nullable=False,
            index=True,
        ),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("sauna_id", "starts_at", name="uq_bookings_slot"),
        sa.CheckConstraint("ends_at > starts_at", name="ck_bookings_time_range"),
    )


def downgrade() -> None:
    op.drop_table("bookings")
    op.drop_table("weekly_turns")
    op.drop_table("saunas")
    op.drop_table("residents")
