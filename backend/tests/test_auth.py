import pytest
from src.app.models.schemas import UserCreate

@pytest.mark.asyncio
async def test_sign_up_success(client):
    """Test successful user sign up"""
    response = await client.post(
        "/api/auth/sign-up",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"
    assert "id" in data

@pytest.mark.asyncio
async def test_sign_up_duplicate_username(client):
    """Test sign up with duplicate username"""
    # First user
    await client.post(
        "/api/auth/sign-up",
        json={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "securepassword123"
        }
    )
    
    # Second user with same username
    response = await client.post(
        "/api/auth/sign-up",
        json={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]

@pytest.mark.asyncio
async def test_sign_in_success(client):
    """Test successful sign in"""
    # Create user first
    await client.post(
        "/api/auth/sign-up",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }
    )
    
    # Sign in
    response = await client.post(
        "/api/auth/sign-in",
        json={
            "username": "testuser",
            "password": "securepassword123"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == "testuser"

@pytest.mark.asyncio
async def test_sign_in_invalid_password(client):
    """Test sign in with invalid password"""
    # Create user
    await client.post(
        "/api/auth/sign-up",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }
    )
    
    # Try sign in with wrong password
    response = await client.post(
        "/api/auth/sign-in",
        json={
            "username": "testuser",
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "Invalid username or password" in response.json()["detail"]
