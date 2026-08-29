"""Tests for health endpoint."""
import pytest


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "service" in data
    assert "version" in data
    assert "database" in data
    assert "ai_provider" in data


def test_health_check_healthy(client):
    response = client.get("/health")
    data = response.json()
    # In test mode with test DB, should be healthy
    assert data["service"] == "NetSage AI"


def test_root_endpoint(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "docs" in data
