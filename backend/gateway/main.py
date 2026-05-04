from routes import auth, ml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from httpx import AsyncClient, Limits

from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = AsyncClient(
        limits=Limits(max_connections=50, max_keepalive_connections=20),
        timeout=20.0
    )
    yield
    # Shutdown
    await app.state.http_client.aclose()

app = FastAPI(
    title="MNIST Character Identifier Gateway",
    description="Gateway for routing requests",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(ml.router, prefix="/api/ml", tags=["ml"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "MNIST Character Identifier Gateway"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.GATEWAY_PORT)
