"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-10-18

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admins",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("login", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login"),
    )
    op.create_table(
        "teachers",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("last_name", sa.String(length=255), nullable=False),
        sa.Column("first_name", sa.String(length=255), nullable=False),
        sa.Column("middle_name", sa.String(length=255), nullable=True),
        sa.Column("uid", sa.String(length=64), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uid"),
    )
    op.create_table(
        "groups",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "schedules",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("academic_year", sa.String(length=16), nullable=False),
        sa.Column("semester", sa.String(length=16), nullable=False),
        sa.Column("pair_number", sa.Integer(), nullable=False),
        sa.Column("course", sa.Integer(), nullable=False),
        sa.Column("lesson_type", sa.String(length=16), nullable=False),
        sa.Column("start_time", sa.Time(), nullable=False),
        sa.Column("end_time", sa.Time(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_schedules_year_semester_pair",
        "schedules",
        ["academic_year", "semester", "pair_number"],
    )
    op.create_table(
        "devices",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("teacher_id", sa.BigInteger(), nullable=False),
        sa.Column("public_key", sa.Text(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_devices_teacher_id", "devices", ["teacher_id"])
    op.create_table(
        "enrollment_codes",
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("teacher_id", sa.BigInteger(), nullable=False),
        sa.Column("created_by_admin", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["created_by_admin"], ["admins.id"]),
        sa.ForeignKeyConstraint(["teacher_id"], ["teachers.id"]),
        sa.PrimaryKeyConstraint("code"),
    )
    op.create_table(
        "pairs",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("schedule_id", sa.BigInteger(), nullable=False),
        sa.Column("room", sa.String(length=64), nullable=False),
        sa.Column("periodicity", sa.String(length=16), nullable=False),
        sa.Column("date_from", sa.Date(), nullable=False),
        sa.Column("date_to", sa.Date(), nullable=False),
        sa.Column("pps_id", sa.BigInteger(), nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.ForeignKeyConstraint(["pps_id"], ["teachers.id"]),
        sa.ForeignKeyConstraint(["schedule_id"], ["schedules.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pairs_pps_group_active", "pairs", ["pps_id", "group_id", "active"])
    op.create_table(
        "students",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("group_id", sa.BigInteger(), nullable=False),
        sa.Column("consent_document", sa.String(length=255), nullable=False),
        sa.Column("consent_date", sa.Date(), nullable=False),
        sa.Column("revocation_document", sa.String(length=255), nullable=True),
        sa.Column("revocation_date", sa.Date(), nullable=True),
        sa.Column("anonymized_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["group_id"], ["groups.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cards",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("uid", sa.String(length=64), nullable=True),
        sa.Column("student_id", sa.BigInteger(), nullable=False),
        sa.Column("active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("uid"),
    )
    op.create_index("ix_cards_student_id", "cards", ["student_id"])
    op.create_table(
        "attendance",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("student_id", sa.BigInteger(), nullable=False),
        sa.Column("pair_id", sa.BigInteger(), nullable=False),
        sa.Column("device_id", sa.String(length=64), nullable=False),
        sa.Column("event_type", sa.String(length=32), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["device_id"], ["devices.id"]),
        sa.ForeignKeyConstraint(["pair_id"], ["pairs.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_attendance_pair_ts", "attendance", ["pair_id", "timestamp"])
    op.create_table(
        "event_log",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column(
            "meta",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "timestamp",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_event_log_timestamp", "event_log", ["timestamp"])
    op.create_index("ix_event_log_severity_ts", "event_log", ["severity", "timestamp"])
    op.create_index("ix_event_log_type_ts", "event_log", ["event_type", "timestamp"])
    op.execute("CREATE INDEX ix_event_log_meta_gin ON event_log USING gin (meta)")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_event_log_meta_gin")
    op.drop_index("ix_event_log_type_ts", table_name="event_log")
    op.drop_index("ix_event_log_severity_ts", table_name="event_log")
    op.drop_index("ix_event_log_timestamp", table_name="event_log")
    op.drop_table("event_log")
    op.drop_index("ix_attendance_pair_ts", table_name="attendance")
    op.drop_table("attendance")
    op.drop_index("ix_cards_student_id", table_name="cards")
    op.drop_table("cards")
    op.drop_table("students")
    op.drop_index("ix_pairs_pps_group_active", table_name="pairs")
    op.drop_table("pairs")
    op.drop_table("enrollment_codes")
    op.drop_index("ix_devices_teacher_id", table_name="devices")
    op.drop_table("devices")
    op.drop_index("ix_schedules_year_semester_pair", table_name="schedules")
    op.drop_table("schedules")
    op.drop_table("groups")
    op.drop_table("teachers")
    op.drop_table("admins")
