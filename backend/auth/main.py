from contextlib import asynccontextmanager

from routes import auth
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from utils.database import init_db
from config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown (if needed) - SQLAlchemy handles cleanup

app = FastAPI(
    title="MNIST Character Identifier Authentication API",
    description="API for user authentication, database operations",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.GATEWAY_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "MNIST Character Identifier API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.AUTH_PORT)
