"""Pytest configuration and fixtures for the FastAPI application tests."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def sample_activities(client):
    """Get the sample activities data."""
    response = client.get("/activities")
    return response.json()
