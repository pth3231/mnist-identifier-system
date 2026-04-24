# MNIST Identifier System

A full-stack app for drawing characters and predicting them with a PyTorch model.

## Quick Start (Docker)

```bash
docker compose up -d
```

- **Frontend** – Next.js on `http://localhost:3000`
- **Backend** – FastAPI on `http://localhost:8000`
- **ML Service** – PyTorch inference on `http://localhost:8001`
- **Database** – PostgreSQL

## Development

| Service | Command |
|---------|---------|
| Backend | `cd backend && uvicorn src.main:app --reload` |
| Frontend | `npm run dev` |

## Testing

```bash
docker compose exec backend pytest
```

## Architecture

- `frontend/` – Next.js app
- `backend/src/app/` – FastAPI app (auth, routes)
- `backend/src/ml/` – PyTorch model & inference service
