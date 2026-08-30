"""
NetSage AI — Test configuration and fixtures.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import get_db
from app.core.database import Base
from app.main import app

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for tests."""
    from app.models import _import_all_models
    _import_all_models()
    Base.metadata.create_all(bind=test_engine)
    db = TestSessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture(scope="function")
def client():
    """Return a test client with test database."""
    from app.models import _import_all_models
    _import_all_models()
    Base.metadata.create_all(bind=test_engine)
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=test_engine)
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def db():
    """Return a test database session."""
    from app.models import _import_all_models
    _import_all_models()
    Base.metadata.create_all(bind=test_engine)
    session = TestSessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    Base.metadata.drop_all(bind=test_engine)


# ---------------------------------------------------------------------------
# Sample data factories
# ---------------------------------------------------------------------------

SAMPLE_CASE_PAYLOAD = {
    "case_id": "TEST-001",
    "category": "STATIC_ROUTING",
    "title": "Test Missing Route",
    "symptom": "PC cannot reach server at 192.168.30.10. Gateway is reachable.",
    "topology": "PC -> SW -> R1 -> Server",
    "show_outputs": {
        "show ip route": (
            "Codes: C - connected, S - static\n"
            "C    192.168.1.0/24 is directly connected, GigabitEthernet0/0\n"
            "C    10.0.0.0/30 is directly connected, GigabitEthernet0/1\n"
        )
    },
    "expected_fault": "Missing route to 192.168.30.0/24",
    "expected_osi_layer": "Layer 3",
    "concept": "Static Routing",
    "severity": "HIGH",
    "expected_fix": ["ip route 192.168.30.0 255.255.255.0 10.0.0.2"],
    "next_command": "show ip route",
    "tags": ["routing", "test"],
}
