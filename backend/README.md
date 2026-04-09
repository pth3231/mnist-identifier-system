# Backend Architecture

This is the FastAPI backend for the Japanese Character Identifier application.

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app setup
│   ├── config.py              # Configuration settings
│   ├── database.py            # Database setup and session management
│   ├── security.py            # JWT and password utilities
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py           # User SQLAlchemy model
│   │   └── schemas.py        # Pydantic request/response schemas
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication endpoints (/sign-up, /sign-in)
│   │   └── predict.py        # Prediction endpoints (HTTP & WebSocket)
│   └── ml/
│       ├── __init__.py
│       ├── model.py          # PyTorch model definition
│       └── predictor.py      # Model inference wrapper
├── tests/
│   ├── __init__.py
│   ├── conftest.py           # pytest configuration
│   ├── test_auth.py          # Authentication tests
│   └── test_predict.py       # Prediction tests
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker container setup
├── .env.example            # Environment variables template
└── README.md               # Backend documentation
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

## Running the Backend

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Run development server
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
Swagger docs: `http://localhost:8000/docs`

### Docker

```bash
# Build image
docker build -t japanese-identifier-backend .

# Run container
docker run -p 8000:8000 \
  -e DATABASE_URL="postgresql://..." \
  -e SECRET_KEY="your-secret-key" \
  japanese-identifier-backend
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
