import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_valid_user():
    payload = {"user_id": "U1", "name": "Alice", "email": "alice@example.com"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["user_id"] == "U1"
    assert data["name"] == "Alice"
    assert data["email"] == "alice@example.com"

def test_create_user_missing_field():

    payload = {"user_id": "U2", "email": "bob@example.com"}
    response = client.post("/users/", json=payload)
    assert response.status_code == 422

def test_get_nonexistent_user():
    response = client.get("/users/not_exists")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()