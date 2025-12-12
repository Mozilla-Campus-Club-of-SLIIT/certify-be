"""API endpoint tests for certify-be.

Note: Tests that require a MongoDB connection are marked with pytest.mark.skip
when running without a database. For full integration tests, run with Docker.
"""

import pytest


def test_root_endpoint(client):
    """Test the root endpoint returns correct message."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Hello, Certify!"


def test_login_missing_credentials(client):
    """Test login endpoint with missing credentials."""
    response = client.post("/api/login", json={})
    assert response.status_code == 400
    assert "Email and password required" in response.json()["detail"]


@pytest.mark.skip(reason="Requires MongoDB connection")
def test_login_invalid_credentials(client):
    """Test login endpoint with invalid credentials."""
    response = client.post("/api/login", json={"email": "invalid@example.com", "password": "wrong"})
    assert response.status_code == 401


@pytest.mark.skip(reason="Requires MongoDB connection")
def test_certificate_not_found(client):
    """Test certificate endpoint with non-existent credential ID."""
    response = client.get("/api/certificate/nonexistent_id")
    assert response.status_code == 404
    assert "Certificate not found" in response.json()["detail"]
