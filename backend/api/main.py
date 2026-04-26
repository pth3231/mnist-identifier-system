from contextlib import asynccontextmanager

from routes import auth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (if needed) - SQLAlchemy handled cleanup

app = FastAPI(
    title="MNIST Character Identifier API",
    description="API for MNIST character recognition with WebSocket streaming",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "MNIST Character Identifier API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
