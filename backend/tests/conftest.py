import os

os.environ["DATABASE_URL"] = "sqlite:///./pathforge_test.db"
os.environ["JWT_SECRET"] = "test-secret-that-is-long-enough-for-safe-jwt-tests"

import pytest
from fastapi.testclient import TestClient

from app.core import settings
from app.database import Base, SessionLocal, engine
from app.main import app


@pytest.fixture(autouse=True)
def use_local_ai_for_tests(monkeypatch):
    # Keep the suite deterministic and avoid real API calls or charges.
    monkeypatch.setattr(settings, "gemini_api_key", None)


@pytest.fixture(autouse=True)
def clean_database():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    session = SessionLocal()
    try: yield session
    finally: session.close()

