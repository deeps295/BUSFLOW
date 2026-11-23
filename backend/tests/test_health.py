import sys
from pathlib import Path

# Add backend directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.database.init_db import init_db
from app.main import root
from app.api.health import health_check
from app.database.session import SessionLocal, engine
from sqlalchemy import inspect
from app.core.security import hash_password, verify_password, create_access_token, decode_access_token

# Initialize tables before running tests
init_db()

def test_root_endpoint():
    data = root()
    assert "BusFlow" in data["message"]
    assert "Sri Eshwar College of Engineering" in data["institution"]
    assert data["docs"] == "/api/docs"

def test_health_endpoint():
    db = SessionLocal()
    try:
        data = health_check(db=db)
        assert data["status"] == "healthy"
        assert data["database"] == "connected"
        assert data["tables_count"] == 11
        assert "Sri Eshwar College of Engineering" in data["institution"]["name"]
        assert data["institution"]["coordinates"]["latitude"] == 10.8284
    finally:
        db.close()

def test_database_models_exist():
    expected_tables = {
        "users",
        "buses",
        "drivers",
        "students",
        "routes",
        "stops",
        "schedules",
        "trips",
        "trip_segments",
        "traffic_reports",
        "model_training_history"
    }
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    assert expected_tables.issubset(existing_tables), f"Missing tables: {expected_tables - existing_tables}"

def test_security_password_hashing():
    pwd = "SecretPassword123!"
    hashed = hash_password(pwd)
    assert hashed != pwd
    assert verify_password(pwd, hashed) is True
    assert verify_password("WrongPassword", hashed) is False

def test_security_jwt_token():
    payload = {"sub": "student_123", "role": "STUDENT"}
    token = create_access_token(payload, expires_delta_minutes=60)
    assert isinstance(token, str)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["sub"] == "student_123"
    assert decoded["role"] == "STUDENT"
