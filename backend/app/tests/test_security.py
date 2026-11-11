import pytest
from datetime import date, datetime, timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base 
from app.services.security_service import SecurityService
from app.schemas_security import StudentCreate, ConsentRevocation

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def security_service(db_session):
    return SecurityService(db_session)

def test_add_student_success(security_service, db_session):
    student_in = StudentCreate(
        full_name="Иванов Иван",
        uid="04:A1:B2:C3",
        group_id=1,
        consent_document="СОГ-001",
        consent_date=date(2024, 1, 1)
    )
    student = security_service.add_student(student_in)
    
    assert student.id is not None
    assert student.full_name == "Иванов Иван"
    assert student.anonymized_at is None

def test_revoke_consent_anonymizes_data(security_service, db_session):
    # Создаем
    student_in = StudentCreate(full_name="Петров Петр", uid="04:D4:E5:F6", group_id=2, consent_document="С01", consent_date=date(2024, 1, 1))
    student = security_service.add_student(student_in)
    
    # Отзываем
    revocation = ConsentRevocation(revocation_document="ОТЗ-001", revocation_date=date(2024, 9, 1))
    updated = security_service.revoke_consent(student.id, revocation)
    
    # Проверяем зануление
    assert updated.full_name is None
    assert updated.uid is None
    assert updated.anonymized_at is not None
    assert updated.revocation_document == "ОТЗ-001"

def test_event_log_pagination(security_service, db_session):
    # Генерируем 5 событий
    for i in range(5):
        security_service._log_event("test_event", "info", {"index": i})
    
    # Запрашиваем первую страницу по 2 записи
    result = security_service.get_event_log(page=1, size=2)
    assert result["total"] == 5
    assert len(result["items"]) == 2
    assert result["page"] == 1
    assert result["size"] == 2