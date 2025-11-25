import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import SessionLocal, engine
from app.db import models

client = TestClient(app)


@pytest.fixture(scope="function")
def auth_token():
    """Create a test user and return auth token"""
    # Register user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "projecttest@example.com",
            "username": "projectuser",
            "password": "testpass123",
        }
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        data={
            "username": "projectuser",
            "password": "testpass123",
        }
    )
    return response.json()["access_token"]


def test_create_project(auth_token):
    """Test creating a project"""
    response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Test Project",
            "description": "Test Description",
            "project_type": "word",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["project_type"] == "word"


def test_list_projects(auth_token):
    """Test listing projects"""
    # Create a project
    client.post(
        "/api/v1/projects/",
        json={
            "name": "List Test Project",
            "project_type": "word",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    
    # List projects
    response = client.get(
        "/api/v1/projects/",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1


def test_get_project(auth_token):
    """Test getting a specific project"""
    # Create a project
    create_response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Get Test Project",
            "project_type": "powerpoint",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    project_id = create_response.json()["id"]
    
    # Get project
    response = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == project_id


def test_update_project(auth_token):
    """Test updating a project"""
    # Create a project
    create_response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Update Test Project",
            "project_type": "word",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    project_id = create_response.json()["id"]
    
    # Update project
    response = client.put(
        f"/api/v1/projects/{project_id}",
        json={
            "name": "Updated Project Name",
            "description": "Updated Description",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Project Name"


def test_delete_project(auth_token):
    """Test deleting a project"""
    # Create a project
    create_response = client.post(
        "/api/v1/projects/",
        json={
            "name": "Delete Test Project",
            "project_type": "word",
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    project_id = create_response.json()["id"]
    
    # Delete project
    response = client.delete(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == 204
    
    # Verify deletion
    get_response = client.get(
        f"/api/v1/projects/{project_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert get_response.status_code == 404

