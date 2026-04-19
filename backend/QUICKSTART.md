# Quick Start Guide

## Installation (5 minutes)

### Step 1: Install Dependencies

```bash
cd backend
pip install -e ".[dev]"
```

### Step 2: Configure Environment

```bash
# Copy environment template
cp .env.example .env
```

Edit `.env` - minimum changes needed:

```env
# For quick testing, use SQLite (no PostgreSQL needed):
DATABASE_URL=sqlite+aiosqlite:///./japanese_identifier.db

# Change the secret key:
SECRET_KEY=change-this-to-a-random-secret-key

# Model path (app will start without it, just won't make predictions):
MODEL_PATH=./models/japanese_classifier.pth
```

### Step 3: Run the Server

```bash
uvicorn src.app.main:app --reload
```

Visit http://localhost:8000/docs for the interactive API documentation.

---

## Quick Test

```bash
# Sign up a new user
curl -X POST http://localhost:8000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@test.com","password":"password123"}'

# Sign in and get token
curl -X POST http://localhost:8000/api/auth/sign-in \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'

# Health check
curl http://localhost:8000/health
```

---

## Running Tests

```bash
pytest -v
```

---

## Alternative: Using Run Scripts

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

---

## Next Steps

1. Set up PostgreSQL for production use
2. Train and add the ML model to `./models/`
3. Configure CORS for your frontend URL
4. Set up HTTPS for production
