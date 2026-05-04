# Agent Instructions: MNIST Identifier System

## Project Context

Build a web application that allows users to draw handwritten digits (0-9) on a 32x32 canvas, export images, and get predictions from a trained ML model. The system is optimized for low latency (500ms-1s) with high throughput (1000 req/s).

## Project Architecture

### Frontend (Next.js)
- **Canvas**: 32x32 drawing area with mouse/pen input
- **Prediction Box**: Shows top 10 digit predictions with confidence scores
- **Read-only Box**: Stores selected digits from predictions
- **Export**: Download canvas as JPEG/PNG image
- **Auth**: Sign-in, Sign-up, Sign-out (username + password only)
- **Color Palette**: #212129, #323949, #3d3e51, #40445a, #4c5265

### Backend Services (Decoupled via Docker)

| Service | Technology | Purpose | Port |
|---------|------------|---------|------|
| **frontend** | Next.js | Web UI | 3000 |
| **api** | FastAPI (Python) | Auth, user management | 8000 |
| **gateway** | Go | HTTP → gRPC bridge for ML | 8080 |
| **ml** | Python (gRPC) | MNIST model inference | 50051 |
| **db** | PostgreSQL | User data persistence | 5432 |
| **redis** | Redis | Token caching, session management | 6379 |
| **rabbitmq** | RabbitMQ | Centralized logging pipeline | 5672/15672 |

### Request Flow
```
User → Frontend → API (auth) → Gateway → ML Service
                   ↘
                    Redis (token cache)
                    
ML Service → RabbitMQ (logging)
```

## ML Model

- **Framework**: PyTorch (CPU optimized)
- **Model**: CNN trained on MNIST dataset
- **Pretrained Weights**: `backend/ml/mnist_trained/mnist_model_fp16.pth`
- **Input**: 28x28 (784 bytes)
- **Output**: Top 10 predictions with confidence scores (0-9)
- **Latency Target**: <100ms inference time

## API Endpoints

### Authentication (`/api/auth`)
- `POST /sign-up` - Create new user (username, email, password)
- `POST /sign-in` - Authenticate user, returns JWT token
- `POST /sign-out` - Invalidate token in Redis
- `GET /me` - Get current user info

### Prediction (`/predict` on Gateway)
- `POST /predict` - Send image data, get digit predictions
- Request: `{ "image_data": "<hex>", "image_width": 32, "image_height": 32 }`
- Response: `{ "predictions": [{"digit": 0, "confidence": 0.95}, ...], "processing_time_ms": 45 }`

### Health Checks
- `GET /health` - Service health status
- `GET /live` - Kubernetes liveness probe

## Data Models

### User
```
id: int (primary key)
username: str (unique)
email: str (unique)
hashed_password: str
is_active: bool (default: true)
created_at: datetime
```

### Redis Keys
- `token:<jwt_token>` → user_id (TTL: 30 minutes)

## Services Configuration

### ML Service
- `ML_MODEL_PATH`: Path to model weights
- `ML_GRPC_PORT`: gRPC server port (default: 50051)

### Gateway
- `ML_SERVICE_ADDR`: ML service address (default: ml:50051)
- `GATEWAY_PORT`: HTTP port (default: 8080)
- `REQUEST_TIMEOUT_MS`: Max request time (default: 5000)
- `MAX_RETRIES`: Retry attempts (default: 2)

### API Service
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string (default: redis://redis:6379/0)
- `SECRET_KEY`: JWT signing key
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token TTL (default: 30)

## Conventions

1. **Separation of Concerns**: Each service is independently deployable
2. **gRPC for ML**: Binary protocol for low-latency inference
3. **No WebSocket**: Using gRPC for synchronous request/response
4. **Redis for Auth Speed**: Cache tokens to reduce DB lookups
5. **RabbitMQ for Logging**: Async log aggregation (not for prediction)
6. **Environment Variables**: All config via `.env` files
7. **Docker-first**: All services containerized for CI/CD

## CI/CD Pipeline

Each service has a `Dockerfile` and can be built independently:

```bash
# Build all services
docker-compose build

# Build individual service
docker build -t mnist-api ./backend/api
docker build -t mnist-gateway ./backend/gateway
docker build -t mnist-ml ./backend/ml
```

### Docker Compose Services
- `db`: PostgreSQL (persistent volume)
- `redis`: Redis (persistent volume)
- `rabbitmq`: RabbitMQ (persistent volume)
- `ml`: gRPC inference server
- `gateway`: HTTP-to-gRPC bridge
- `api`: FastAPI authentication service
- `frontend`: Next.js application

## Tests

### Backend (pytest)
- `test_auth.py`: Sign-in (empty, wrong credentials, correct), Sign-up
- `test_predict.py`: Gateway prediction endpoint

### Frontend
- Component testing with Playwright

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js, TypeScript, TailwindCSS |
| Backend API | FastAPI, SQLAlchemy (async), Pydantic |
| ML Service | PyTorch, grpcio |
| Gateway | Go, grpc-go |
| Database | PostgreSQL 15+ |
| Cache | Redis 7+ |
| Message Queue | RabbitMQ 3 |
| Container | Docker, Docker Compose |

## Architecture Diagram

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│  User   │────▶│Frontend │────▶│   API   │────▶│  Redis  │
└─────────┘     └────┬────┘     └────┬────┘     └─────────┘
                     │              │
                     │              │ (JWT verified)
                     │              ▼
                     │         ┌─────────┐
                     │         │   DB    │
                     │         └─────────┘
                     │
                     ▼
              ┌─────────────┐     ┌─────────────┐
              │  Gateway    │────▶│  ML Service │
              │  (Go)       │     │  (gRPC)     │
              └─────────────┘     └─────────────┘
                                        │
                                        ▼ (logging)
                                   ┌───────────┐
                                   │ RabbitMQ  │
                                   └───────────┘
```

## Performance Requirements

| Metric | Target |
|--------|--------|
| End-to-end latency | <1s (P99) |
| ML inference time | <100ms |
| Throughput | 1000 req/s |
| Availability | 99.9% |

## Future Improvements (if needed)

1. **Batch Inference**: Queue requests for batch processing (throughput boost)
2. **GPU Acceleration**: Enable CUDA for faster inference
3. **Horizontal Scaling**: Multiple ML instances behind load balancer
4. **Model Versioning**: A/B testing for different model versions
5. **Observability**: Prometheus metrics + Grafana dashboards