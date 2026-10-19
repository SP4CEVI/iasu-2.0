from datetime import date, datetime, time

from sqlalchemy import (
    BigInteger,
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    Time,
    func,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    login: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    middle_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    uid: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    devices: Mapped[list["Device"]] = relationship(back_populates="teacher")
    pairs: Mapped[list["Pair"]] = relationship(back_populates="pps")

    @property
    def display_name(self) -> str:
        parts = [self.last_name, self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        return " ".join(parts)


class Device(Base):
    __tablename__ = "devices"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), nullable=False, index=True)
    public_key: Mapped[str] = mapped_column(Text, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    teacher: Mapped["Teacher"] = relationship(back_populates="devices")


class EnrollmentCode(Base):
    __tablename__ = "enrollment_codes"

    code: Mapped[str] = mapped_column(String(64), primary_key=True)
    teacher_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), nullable=False)
    created_by_admin: Mapped[int] = mapped_column(ForeignKey("admins.id"), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)

    students: Mapped[list["Student"]] = relationship(back_populates="group")
    pairs: Mapped[list["Pair"]] = relationship(back_populates="group")


class Schedule(Base):
    """Расписание пар: слот в учебном году/семестре."""

    __tablename__ = "schedules"
    __table_args__ = (
        Index(
            "ix_schedules_year_semester_pair",
            "academic_year",
            "semester",
            "pair_number",
        ),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    academic_year: Mapped[str] = mapped_column(String(16), nullable=False)  # 2026/27
    semester: Mapped[str] = mapped_column(String(16), nullable=False)  # autumn | spring
    pair_number: Mapped[int] = mapped_column(Integer, nullable=False)
    course: Mapped[int] = mapped_column(Integer, nullable=False)
    lesson_type: Mapped[str] = mapped_column(String(16), nullable=False)  # ЛР, ПЗ, ЛК…
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    pairs: Mapped[list["Pair"]] = relationship(back_populates="schedule")


class Pair(Base):
    """Пара (занятие): замена subjects + teacher_subjects."""

    __tablename__ = "pairs"
    __table_args__ = (Index("ix_pairs_pps_group_active", "pps_id", "group_id", "active"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    schedule_id: Mapped[int] = mapped_column(ForeignKey("schedules.id"), nullable=False)
    room: Mapped[str] = mapped_column(String(64), nullable=False)
    periodicity: Mapped[str] = mapped_column(String(16), nullable=False)  # weekly | biweekly | once
    date_from: Mapped[date] = mapped_column(Date, nullable=False)
    date_to: Mapped[date] = mapped_column(Date, nullable=False)
    pps_id: Mapped[int] = mapped_column(ForeignKey("teachers.id"), nullable=False)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    schedule: Mapped["Schedule"] = relationship(back_populates="pairs")
    pps: Mapped["Teacher"] = relationship(back_populates="pairs")
    group: Mapped["Group"] = relationship(back_populates="pairs")


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    consent_document: Mapped[str] = mapped_column(String(255), nullable=False)
    consent_date: Mapped[date] = mapped_column(Date, nullable=False)
    revocation_document: Mapped[str | None] = mapped_column(String(255), nullable=True)
    revocation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    anonymized_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    group: Mapped["Group"] = relationship(back_populates="students")
    cards: Mapped[list["Card"]] = relationship(back_populates="student")


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    uid: Mapped[str | None] = mapped_column(String(64), unique=True, nullable=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    student: Mapped["Student"] = relationship(back_populates="cards")


class Attendance(Base):
    __tablename__ = "attendance"
    __table_args__ = (Index("ix_attendance_pair_ts", "pair_id", "timestamp"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False)
    pair_id: Mapped[int] = mapped_column(ForeignKey("pairs.id"), nullable=False)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.id"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(32), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    student: Mapped["Student"] = relationship()
    pair: Mapped["Pair"] = relationship()


class EventLog(Base):
    __tablename__ = "event_log"
    __table_args__ = (
        Index("ix_event_log_timestamp", "timestamp"),
        Index("ix_event_log_severity_ts", "severity", "timestamp"),
        Index("ix_event_log_type_ts", "event_type", "timestamp"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    event_type: Mapped[str] = mapped_column(String(64), nullable=False)
    severity: Mapped[str] = mapped_column(String(32), nullable=False)
    meta: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )


# Стандартные интервалы пар: 90 мин + перерыв 15 мин (после 2-й — обед до 13:00)
PAIR_TIMES: dict[int, tuple[time, time]] = {
    1: (time(9, 0), time(10, 30)),
    2: (time(10, 45), time(12, 15)),
    3: (time(13, 0), time(14, 30)),
    4: (time(14, 45), time(16, 15)),
    5: (time(16, 30), time(18, 0)),
    6: (time(18, 15), time(19, 45)),
    7: (time(20, 0), time(21, 30)),
}
