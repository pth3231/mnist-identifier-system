from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import auth, predict
from .database import init_db

app = FastAPI(
    title="Japanese Character Identifier API",
    description="API for Japanese character recognition with WebSocket streaming",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure based on frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
@app.on_event("startup")
async def startup_event():
    await init_db()

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(predict.router, prefix="/api", tags=["predict"])

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Japanese Character Identifier API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
