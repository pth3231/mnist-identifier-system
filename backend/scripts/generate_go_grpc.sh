#!/bin/bash
# Generate Go gRPC code from proto files
# Usage: ./scripts/generate_go_grpc.sh

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"
GRPC_DIR="$REPO_ROOT/grpc"
PROTO_DIR="$REPO_ROOT/backend/gateway/proto"

echo "Generating Go gRPC code from proto files..."
echo "Proto source: $GRPC_DIR"
echo "Proto destination: $PROTO_DIR"

mkdir -p "$PROTO_DIR"

# Install tools if needed
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest

# Generate MNIST service
protoc \
    --go_out="$PROTO_DIR" --go_opt=paths=source_relative \
    --go-grpc_out="$PROTO_DIR" --go-grpc_opt=paths=source_relative \
    -I"$GRPC_DIR" \
    "$GRPC_DIR/mnist_service.proto"

# Generate Logging service
protoc \
    --go_out="$PROTO_DIR" --go_opt=paths=source_relative \
    --go-grpc_out="$PROTO_DIR" --go-grpc_opt=paths=source_relative \
    -I"$GRPC_DIR" \
    "$GRPC_DIR/logging_service.proto"

echo "✓ Go gRPC code generation complete!"
echo "Generated files in: $PROTO_DIR"
