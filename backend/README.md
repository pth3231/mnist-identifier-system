# Japanese Character Identifier - Backend

FastAPI backend for the Japanese Character Identifier application with JWT authentication, PostgreSQL database, and PyTorch-based character recognition.

## Quick Start

```bash
# From the backend directory

# Option 1: Using pip (recommended for development)
pip install -e ".[dev]"

# Option 2: Using uv (faster alternative)
uv pip install -e ".[dev]"

# Set up environment
cp .env.example .env
# Edit .env with your configuration

# Run the server
uvicorn src.app.main:app --reload
```

The API will be available at `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Project Structure

```
backend/
├── src/
│   └── app/
│       ├── __init__.py
│       ├── main.py                 # FastAPI app setup & CORS
│       ├── config.py              # Pydantic settings management
│       ├── database.py            # Async SQLAlchemy setup
│       ├── security.py            # JWT & password hashing
│       ├── models/
│       │   ├── __init__.py
│       │   ├── user.py           # User ORM model
│       │   └── schemas.py        # Pydantic schemas
│       ├── routes/
│       │   ├── __init__.py
│       │   ├── auth.py           # Auth endpoints
│       │   └── predict.py        # Prediction endpoints
│       └── ml/
│           ├── __init__.py
│           ├── model.py          # PyTorch model
│           └── predictor.py      # Inference wrapper
├── tests/
│   ├── conftest.py               # pytest fixtures
│   ├── test_auth.py
│   └── test_predict.py
├── pyproject.toml                # Package configuration
├── .env.example                  # Environment template
├── Dockerfile
└── README.md
```

## Implemented Components

### Authentication (`app/routes/auth.py`)
- **POST /api/auth/sign-up**: Register new user
  - Validates: username (3-50 chars), email, password (6+ chars)
  - Returns: User info with id, created_at
  
- **POST /api/auth/sign-in**: User login
  - Returns: JWT access token + user info

### Prediction (`app/routes/predict.py`)
- **WebSocket /api/ws/predict/{client_id}**: Real-time streaming predictions
  - Accepts: 96x96 grayscale image data (9216 bytes)
  - Returns: Top 15 character predictions with confidence
  
- **POST /api/predict**: Single prediction (requires auth token)
  - Returns: Prediction results

### ML Model (`app/ml/`)
- **JapaneseCharacterClassifier**: PyTorch model
  - Input: 96x96 flattened grayscale image (9216 features)
  - Output: 3036 class probabilities (ETL9G dataset)
  - Architecture: 4 fully connected layers with dropout
  
- **Predictor**: Model inference wrapper with preprocessing

### Database (`app/models/user.py`)
- User model with username, email, password
- Timestamps for tracking user lifecycle

### Security (`app/security.py`)
- Password hashing with bcrypt
- JWT token generation and verification
- Bearer token authentication

## Installation and Running

### Prerequisites

- Python 3.10 or higher
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
