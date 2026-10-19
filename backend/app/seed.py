"""Seed reference data and default admin. Safe to run multiple times."""

import os
import secrets
import sys
from datetime import date

from sqlalchemy import select

from app.database import SessionLocal
from app.models import PAIR_TIMES, Admin, Group, Pair, Schedule, Teacher
from app.services.auth_admin import hash_password


def seed() -> None:
    db = SessionLocal()
    try:
        groups = ["ИУ7-21", "ИУ7-22", "ИУ6-31"]
        for name in groups:
            if not db.scalar(select(Group).where(Group.name == name)):
                db.add(Group(name=name))
        db.flush()

        teachers = [
            {
                "last_name": "Иванов",
                "first_name": "Пётр",
                "middle_name": "Сергеевич",
                "uid": "ext-teacher-001",
            },
            {
                "last_name": "Сидорова",
                "first_name": "Анна",
                "middle_name": "Викторовна",
                "uid": "ext-teacher-002",
            },
        ]
        for t in teachers:
            if not db.scalar(select(Teacher).where(Teacher.uid == t["uid"])):
                db.add(Teacher(**t, active=True))
        db.flush()

        # Расписание: 1–3 пары осеннего семестра 2026/27
        schedule_specs = [
            {"pair_number": 1, "course": 2, "lesson_type": "ЛК"},
            {"pair_number": 2, "course": 2, "lesson_type": "ПЗ"},
            {"pair_number": 3, "course": 2, "lesson_type": "ЛР"},
        ]
        schedules: list[Schedule] = []
        for spec in schedule_specs:
            start, end = PAIR_TIMES[spec["pair_number"]]
            existing = db.scalar(
                select(Schedule).where(
                    Schedule.academic_year == "2026/27",
                    Schedule.semester == "autumn",
                    Schedule.pair_number == spec["pair_number"],
                    Schedule.course == spec["course"],
                    Schedule.lesson_type == spec["lesson_type"],
                )
            )
            if existing:
                schedules.append(existing)
            else:
                row = Schedule(
                    academic_year="2026/27",
                    semester="autumn",
                    pair_number=spec["pair_number"],
                    course=spec["course"],
                    lesson_type=spec["lesson_type"],
                    start_time=start,
                    end_time=end,
                )
                db.add(row)
                db.flush()
                schedules.append(row)

        teacher1 = db.scalar(select(Teacher).where(Teacher.uid == teachers[0]["uid"]))
        teacher2 = db.scalar(select(Teacher).where(Teacher.uid == teachers[1]["uid"]))
        group1 = db.scalar(select(Group).where(Group.name == groups[0]))
        group2 = db.scalar(select(Group).where(Group.name == groups[1]))

        pair_specs = [
            {
                "name": "Математика",
                "schedule": schedules[0],
                "room": "301л",
                "periodicity": "weekly",
                "pps": teacher1,
                "group": group1,
            },
            {
                "name": "Математика",
                "schedule": schedules[0],
                "room": "301л",
                "periodicity": "weekly",
                "pps": teacher1,
                "group": group2,
            },
            {
                "name": "Программирование",
                "schedule": schedules[2],
                "room": "505",
                "periodicity": "biweekly",
                "pps": teacher2,
                "group": group2,
            },
        ]
        for p in pair_specs:
            exists = db.scalar(
                select(Pair).where(
                    Pair.name == p["name"],
                    Pair.schedule_id == p["schedule"].id,
                    Pair.pps_id == p["pps"].id,
                    Pair.group_id == p["group"].id,
                )
            )
            if not exists:
                db.add(
                    Pair(
                        name=p["name"],
                        schedule_id=p["schedule"].id,
                        room=p["room"],
                        periodicity=p["periodicity"],
                        date_from=date(2026, 9, 1),
                        date_to=date(2026, 12, 31),
                        pps_id=p["pps"].id,
                        group_id=p["group"].id,
                        active=True,
                    )
                )

        login = os.environ.get("ADMIN_DEFAULT_LOGIN", "admin")
        admin = db.scalar(select(Admin).where(Admin.login == login))
        if admin is None:
            password = os.environ.get("ADMIN_DEFAULT_PASSWORD") or secrets.token_urlsafe(12)
            db.add(
                Admin(
                    login=login,
                    password_hash=hash_password(password),
                    active=True,
                )
            )
            db.commit()
            print("=" * 43)
            print(" Создан администратор")
            print(f" Логин: {login}")
            print(f" Пароль: {password}")
            print(" Сохраните пароль — он показан один раз.")
            print("=" * 43)
        else:
            db.commit()
            print("Seed: admin already exists, reference data ensured.")
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    try:
        seed()
    except Exception as exc:
        print(f"Seed failed: {exc}", file=sys.stderr)
        raise
