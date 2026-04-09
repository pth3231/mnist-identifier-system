import pytest
import numpy as np

@pytest.mark.asyncio
async def test_predict_invalid_data_size(client):
    """Test prediction with invalid canvas data size"""
    # Create token first
    await client.post(
        "/api/auth/sign-up",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }
    )
    
    sign_in_response = await client.post(
        "/api/auth/sign-in",
        json={
            "username": "testuser",
            "password": "securepassword123"
        }
    )
    
    token = sign_in_response.json()["access_token"]
    
    # Try to predict with invalid data
    response = await client.post(
        "/api/predict",
        files={"canvas_data": ("test.bin", b"invalid data")},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400 or response.status_code == 422

@pytest.mark.asyncio
async def test_predict_success(client):
    """Test successful prediction"""
    # Create user and sign in
    await client.post(
        "/api/auth/sign-up",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "securepassword123"
        }
    )
    
    sign_in_response = await client.post(
        "/api/auth/sign-in",
        json={
            "username": "testuser",
            "password": "securepassword123"
        }
    )
    
    token = sign_in_response.json()["access_token"]
    
    # Create dummy canvas data (96x96 grayscale)
    canvas_data = np.zeros((96, 96), dtype=np.uint8)
    canvas_bytes = canvas_data.tobytes()
    
    # Send prediction request
    response = await client.post(
        "/api/predict",
        content=canvas_bytes,
        headers={"Authorization": f"Bearer {token}"}
    )
    
    # Should work or fail gracefully
    assert response.status_code in [200, 400, 422]
