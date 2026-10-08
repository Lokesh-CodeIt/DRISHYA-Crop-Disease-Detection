"""
main.py - LeafLens FastAPI Application Entrypoint

LeafLens: Explainable Disease Detection in Turmeric and Citrus Crops Using Deep Learning
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import api_router
from .utils.config import settings
from .services.inference_service import inference_service
from .db.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("LeafLens.Main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    logger.info("Initializing LeafLens Backend...")
    init_db()
    inference_service.initialize_models()
    yield
    logger.info("LeafLens Backend Shutting Down...")



app = FastAPI(
    title="LeafLens API",
    description="Explainable Disease Detection in Turmeric and Citrus Crops with Calibrated Confidence",
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(api_router, prefix="/api")  # Convenience alias


@app.get("/", tags=["Root"])
def root():
    return {
        "project": "LeafLens",
        "description": "Explainable Disease Detection in Turmeric and Citrus Crops",
        "version": settings.VERSION,
        "docs": "/docs",
        "status": "online",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
