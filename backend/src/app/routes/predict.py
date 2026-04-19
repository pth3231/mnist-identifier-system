from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Body
from ..ml.predictor import get_predictor
from ..models.schemas import PredictionResponse, PredictionResult
from ..security import verify_token
import numpy as np
from PIL import Image

router = APIRouter()

@router.websocket("/ws/predict/{client_id}")
async def websocket_predict_endpoint(websocket: WebSocket, client_id: str):
    """
    WebSocket endpoint for real-time prediction.
    
    Expected message format:
    {
        "canvas_data": bytes (base64 encoded 96x96 grayscale image)
    }
    
    Response format:
    {
        "predictions": [
            {"character": "str", "confidence": float},
            ...
        ]
    }
    """
    await websocket.accept()
    predictor = get_predictor()
    
    try:
        while True:
            # Receive canvas data from client
            data = await websocket.receive_bytes()
            
            if not data or len(data) != 9216:  # 96 * 96 * 1 byte (grayscale)
                await websocket.send_json({
                    "error": "Invalid canvas data. Expected 9216 bytes (96x96 grayscale image)"
                })
                continue
            
            # Parse canvas data
            canvas_array = np.frombuffer(data, dtype=np.uint8)
            canvas_array = canvas_array.reshape(96, 96)
            
            # Get predictions from model
            predictions = predictor.predict(canvas_array)
            
            # Format response
            response = {
                "predictions": [
                    {
                        "character": pred["character"],
                        "confidence": float(pred["confidence"])
                    }
                    for pred in predictions
                ]
            }
            
            await websocket.send_json(response)
            
    except WebSocketDisconnect:
        print(f"Client {client_id} disconnected")
    except Exception as e:
        await websocket.send_json({"error": str(e)})
        await websocket.close(code=status.WS_1011_SERVER_ERROR)

@router.post("/predict", response_model=PredictionResponse)
async def predict(
    request: PredictionRequest = Body(...),
    token: dict = Depends(verify_token)
):
    """
    HTTP endpoint for single prediction.

    Requires authentication token.
    """
    canvas_data = request.canvas_data

    if not canvas_data or len(canvas_data) != 9216:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid canvas data. Expected 9216 bytes (96x96 grayscale image)"
        )

    try:
        # Parse canvas data
        canvas_array = np.frombuffer(canvas_data, dtype=np.uint8)
        canvas_array = canvas_array.reshape(96, 96)

        # Get predictions
        predictor = get_predictor()
        predictions = predictor.predict(canvas_array)

        return PredictionResponse(
            predictions=[
                PredictionResult(
                    character=pred["character"],
                    confidence=pred["confidence"]
                )
                for pred in predictions
            ]
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction failed: {str(e)}"
        )
