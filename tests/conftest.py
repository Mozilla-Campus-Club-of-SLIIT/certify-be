"""Pytest configuration and fixtures for certify-be tests."""

import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_certificate():
    """Return a mock certificate document for testing."""
    return {
        "_id": "test_id_123",
        "credentialId": "test_cred_123",
        "name": "Test User",
        "course": "Test Course",
        "categoryCode": "TEST",
        "categoryName": "Test Category",
        "dateIssued": "2025-01-01",
        "issuer": "Test Issuer",
        "signatures": [],
    }
