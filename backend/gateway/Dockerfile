FROM golang:1.21-alpine AS builder

WORKDIR /app

# Install protobuf compiler
RUN apk add --no-cache protobuf-dev

COPY go.mod go.sum* ./

RUN go mod download

# Copy and generate proto files from grpc/ folder
COPY grpc/ ./grpc/
RUN mkdir -p proto && \
    go install google.golang.org/protobuf/cmd/protoc-gen-go@latest && \
    go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest && \
    protoc \
    --go_out=./proto --go_opt=paths=source_relative \
    --go-grpc_out=./proto --go-grpc_opt=paths=source_relative \
    -I./grpc \
    ./grpc/mnist_service.proto ./grpc/logging_service.proto

COPY . .

# Build binary
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o gateway .

# Final stage
FROM alpine:latest

RUN apk --no-cache add ca-certificates curl

WORKDIR /root/

COPY --from=builder /app/gateway .

EXPOSE 8080

ENV ML_SERVICE_ADDR=ml:50051 \
    GATEWAY_PORT=8080 \
    REQUEST_TIMEOUT_MS=5000 \
    MAX_RETRIES=2

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

CMD ["./gateway"]
