# MNIST Identifier - Backend

FastAPI backend with JWT auth and PyTorch inference.

## Quick Start

```bash
pip install -e ".[dev]"
cp .env.example .env
uvicorn src.app.main:app --reload
```

API docs: `http://localhost:8000/docs`

## Structure

```
app/
├── main.py          # FastAPI app
├── config.py        # Settings
├── database.py      # Async SQLAlchemy
├── security.py      # JWT & password hashing
├── models/          # ORM & schemas
└── routes/          # auth, predict
tests/
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/sign-up` | Register user |
| POST | `/api/auth/sign-in` | Login, returns JWT |
| WS | `/api/ws/predict/{id}` | Real-time prediction |
| POST | `/api/predict` | Single prediction (auth required) |
- PostgreSQL 14+ (for production) or SQLite (for development/testing)

### Step 1: Install Dependencies

**Option A: Using pip (recommended)**
```bash
cd backend
pip install -e ".[dev]"
```

**Option B: Using requirements.txt**
```bash
pip install -r requirements.txt
# For development: pip install -r requirements.txt && pip install pytest pytest-asyncio httpx aiosqlite
```

**Option C: Using uv (fast alternative)**
```bash
pip install uv
uv pip install -e ".[dev]"
```

### Step 2: Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your settings
# Required settings:
#   - DATABASE_URL: Your PostgreSQL connection string
#   - SECRET_KEY: A secure random string for JWT
#   - MODEL_PATH: Path to your trained PyTorch model
```

**Minimum .env configuration:**
```env
# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/japanese_identifier

# Or for SQLite (development only)
# DATABASE_URL=sqlite+aiosqlite:///./japanese_identifier.db

# Security (generate a secure key: openssl rand -hex 32)
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# ML Model
MODEL_PATH=./models/japanese_classifier.pth

# API
FRONTEND_URL=http://localhost:3000
```

### Step 3: Run the Server

**Development mode (with auto-reload):**
```bash
uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Using the installed CLI:**
```bash
japanese-api  # Runs via entry point defined in pyproject.toml
```

### Docker Deployment

```bash
# Build the image
docker build -t japanese-identifier-backend .

# Run with environment variables
docker run -d \
  --name japanese-api \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql://user:password@host:5432/dbname" \
  -e SECRET_KEY="your-secret-key" \
  japanese-identifier-backend

# Or using docker-compose (if available)
docker-compose up -d
```

## API Endpoints

### Authentication
- `POST /api/auth/sign-up` - Register new user
- `POST /api/auth/sign-in` - Login user

### Prediction
- `WebSocket /api/ws/predict/{client_id}` - Stream predictions
- `POST /api/predict` - Single prediction (auth required)

### Health Check
- `GET /health` - Service health status

## Testing

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth.py

# Run with verbose output
pytest -v
```

## Next Steps

1. **ML Model Training**: Train PyTorch model on ETL9G dataset
2. **Database Migration**: Set up PostgreSQL and apply migrations
3. **Character Mapping**: Load actual character labels for ETL9G dataset
4. **API Documentation**: Complete Swagger documentation
5. **Error Handling**: Enhanced error messages and logging
6. **CI/CD**: GitHub Actions or GitLab CI pipeline
