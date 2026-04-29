FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ML_MODEL_PATH=/models/mnist_trained/mnist_model_fp16.pth \
    ML_GRPC_PORT=50051

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./

RUN pip install --upgrade pip setuptools && \
    pip install torch --index-url https://download.pytorch.org/whl/cpu

RUN pip install -e . && \
    pip install grpcio-tools

# Copy proto file and generate gRPC code
COPY grpc/ ./grpc/
RUN python -m grpc_tools.protoc \
    -I./grpc \
    --python_out=. \
    --grpc_python_out=. \
    ./grpc/mnist_service.proto

# Copy pretrained model
COPY backend/ml/mnist_trained/ /models/mnist_trained/

EXPOSE 50051

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD python -c "import socket; socket.create_connection(('localhost', 50051), timeout=5)" || exit 1

CMD ["python", "main.py"]