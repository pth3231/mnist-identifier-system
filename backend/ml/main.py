"""
gRPC server for MNIST digit prediction service.
Handles model loading, inference, and serves predictions via gRPC.
"""

import logging
import asyncio
import time
from pathlib import Path
from typing import List
import os

import grpc
import numpy as np
import torch
import torchvision.transforms as transforms
from grpc import aio

# Import generated proto files
import sys
sys.path.insert(0, str(Path(__file__).parent))
from mnist_service_pb2 import (
    PredictionRequest,
    PredictionResponse,
    Prediction,
    HealthCheckRequest,
    HealthCheckResponse,
)
import mnist_service_pb2_grpc

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class MnistModel:
    """Wrapper for MNIST PyTorch model."""
    
    def __init__(self, model_path: str, device: str = "cpu"):
        """Initialize model and load weights."""
        self.device = torch.device(device)
        self.model_path = model_path
        self.model_version = "1.0.0-fp16"
        
        # Define model architecture (must match training)
        self.model = self._build_model()
        self.load_model()
        
        # Preprocessing transforms
        self.transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize((0.1307,), (0.3081,))  # MNIST std normalization
        ])
        
        logger.info(f"Model initialized on device: {self.device}")
    
    def _build_model(self):
        """Define the neural network architecture."""
        # Simple CNN for MNIST - matches training architecture
        model = torch.nn.Sequential(
            torch.nn.Conv2d(1, 32, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2, 2),
            torch.nn.Conv2d(32, 64, kernel_size=3, padding=1),
            torch.nn.ReLU(),
            torch.nn.MaxPool2d(2, 2),
            torch.nn.Flatten(),
            torch.nn.Linear(64 * 7 * 7, 128),
            torch.nn.ReLU(),
            torch.nn.Dropout(0.5),
            torch.nn.Linear(128, 10)
        )
        return model.to(self.device)
    
    def load_model(self):
        """Load model weights from file."""
        if not Path(self.model_path).exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        
        try:
            state_dict = torch.load(self.model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.eval()
            logger.info(f"Model loaded from {self.model_path}")
            logger.info(f"Model architecture: {self.model}")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def preprocess(self, image_data: bytes, width: int = 0, height: int = 0) -> torch.Tensor:
        """
        Preprocess image data for inference.
        
        Handles both 28x28 (784 bytes) and 96x96 (9216 bytes) images.
        Automatically detects dimensions if not provided.
        """
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        
        # Detect or validate dimensions
        if width == 0 or height == 0:
            if len(image_array) == 784:
                width, height = 28, 28
            elif len(image_array) == 9216:
                width, height = 96, 96
            else:
                raise ValueError(f"Unexpected image size: {len(image_array)} bytes")
        
        # Reshape to 2D image
        image_array = image_array.reshape(height, width)
        
        # Resize to 28x28 if needed (model expects 28x28)
        if height != 28 or width != 28:
            from PIL import Image
            img = Image.fromarray(image_array, mode='L')
            img = img.resize((28, 28), Image.LANCZOS)
            image_array = np.array(img)
        
        # Convert to tensor and normalize
        image_tensor = torch.from_numpy(image_array).float().unsqueeze(0).unsqueeze(0)
        image_tensor = image_tensor / 255.0  # Normalize to [0, 1]
        image_tensor = image_tensor.to(self.device)
        
        return image_tensor
    
    def predict(self, image_data: bytes, width: int = 0, height: int = 0) -> List[tuple]:
        """
        Perform inference and return top predictions.
        
        Returns list of (digit, confidence) tuples sorted by confidence descending.
        """
        with torch.no_grad():
            image_tensor = self.preprocess(image_data, width, height)
            logits = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            
            # Get top predictions
            probs, indices = torch.topk(probabilities[0], k=10)
            
            predictions = [
                (int(idx.item()), float(prob.item()))
                for idx, prob in zip(indices, probs)
            ]
        
        return predictions


class MnistServicer(mnist_service_pb2_grpc.MnistServiceServicer):
    """gRPC servicer for MNIST predictions."""
    
    def __init__(self, model: MnistModel):
        self.model = model
    
    async def Predict(self, request: PredictionRequest, context: grpc.aio.ServicerContext) -> PredictionResponse:
        """Handle prediction requests."""
        try:
            start_time = time.time()
            
            logger.info(f"Received prediction request with {len(request.image_data)} bytes")
            
            # Perform inference
            predictions = self.model.predict(
                request.image_data,
                width=request.image_width,
                height=request.image_height
            )
            
            processing_time_ms = int((time.time() - start_time) * 1000)
            
            # Build response
            response = PredictionResponse(
                predictions=[
                    Prediction(digit=digit, confidence=confidence)
                    for digit, confidence in predictions
                ],
                processing_time_ms=processing_time_ms,
                model_version=self.model.model_version
            )
            
            logger.info(
                f"Prediction completed in {processing_time_ms}ms. "
                f"Top digit: {predictions[0][0]} ({predictions[0][1]:.2%})"
            )
            
            return response
        
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            await context.abort(grpc.StatusCode.INTERNAL, f"Prediction failed: {str(e)}")
    
    async def Health(self, request: HealthCheckRequest, context: grpc.aio.ServicerContext) -> HealthCheckResponse:
        """Health check endpoint."""
        return HealthCheckResponse(
            status=HealthCheckResponse.ServingStatus.SERVING,
            message="MNIST service is healthy",
            model_version=self.model.model_version
        )


async def serve():
    """Start the gRPC server."""
    # Get model path from environment (defaults to pretrained weights)
    model_path = os.environ.get(
        "ML_MODEL_PATH",
        "/models/mnist_trained/mnist_model_fp16.pth"
    )
    
    # Check if GPU is available
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")
    
    # Load model
    logger.info(f"Loading model from {model_path}")
    model = MnistModel(model_path, device=device)
    
    # Create servicer
    servicer = MnistServicer(model)
    
    # Create server
    server = aio.Server()
    mnist_service_pb2_grpc.add_MnistServiceServicer_to_server(servicer, server)
    
    # Bind to port
    port = os.environ.get("ML_GRPC_PORT", "50051")
    listen_addr = f"[::]:{port}"
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    logger.info("gRPC server started successfully")
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
        await server.stop(0)


if __name__ == "__main__":
    asyncio.run(serve())
