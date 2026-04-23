# MNIST Identifier System

A minimal full‑stack app that lets users draw Japanese characters, predicts the character with a PyTorch model, and shows confidence scores.

## Quick start (Docker)
```bash
docker compose up -d   # build and run all services
```

* **Backend** – FastAPI on `http://localhost:8000`
* **Frontend** – Next.js on `http://localhost:3000`
* **Database** – PostgreSQL (data persisted in `postgres_data` volume)

## Development
* Backend code lives in `backend/src`. Run with:
```bash
uvicorn src.main:app --reload
```
* Frontend code lives in the repo root. Start with:
```bash
npm run dev
```

## Tests
```bash
docker compose exec backend pytest
```

## License
Creative Commons Attribution Non Commercial 4.0 International - CC-BY-NC-4.0
