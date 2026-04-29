#!/bin/bash
# Generate Python gRPC code from proto files
# Usage: ./scripts/generate_python_grpc.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
GRPC_DIR="$REPO_ROOT/grpc"

echo "Generating Python gRPC code from proto files..."
echo "gRPC directory: $GRPC_DIR"

# Generate MNIST service
python -m grpc_tools.protoc \
    -I"$GRPC_DIR" \
    --python_out="$REPO_ROOT/backend/ml" \
    --grpc_python_out="$REPO_ROOT/backend/ml" \
    "$GRPC_DIR/mnist_service.proto"

# Generate Logging service
python -m grpc_tools.protoc \
    -I"$GRPC_DIR" \
    --python_out="$REPO_ROOT/backend/ml" \
    --grpc_python_out="$REPO_ROOT/backend/ml" \
    "$GRPC_DIR/logging_service.proto"

echo "✓ Python gRPC code generation complete!"
echo "Generated files:"
echo "  - backend/ml/mnist_service_pb2.py"
echo "  - backend/ml/mnist_service_pb2_grpc.py"
echo "  - backend/ml/logging_service_pb2.py"
echo "  - backend/ml/logging_service_pb2_grpc.py"
