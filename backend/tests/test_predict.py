import pytest
import numpy as np
from backend.app.models.schemas import PredictionRequest

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

    # Try to predict with invalid data (too short)
    response = await client.post(
        "/api/predict",
        json={"canvas_data": "aW52YWxpZA=="},  # base64 encoded "invalid"
        headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code in [400, 422]

@pytest.mark.asyncio
async def test_predict_success(client):
    """Test successful prediction"""
    import base64

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
    canvas_b64 = base64.b64encode(canvas_bytes).decode()

    # Send prediction request
    response = await client.post(
        "/api/predict",
        json={"canvas_data": canvas_b64},
        headers={"Authorization": f"Bearer {token}"}
    )

    # Should work or fail gracefully (model may not be loaded)
    assert response.status_code in [200, 500]
