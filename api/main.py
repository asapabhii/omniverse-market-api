"""
Omniverse Market API - FastAPI Main Application
Author: Abhi
Email: dankalu.work@gmail.com

A production-ready API-first engine for ingesting and normalizing
Kalshi and Polymarket data for forecasting and trading models.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routes import ingest, markets

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup/shutdown events."""
    logger.info("Starting Omniverse Market API...")
    yield
    logger.info("Shutting down Omniverse Market API...")


def create_envelope(data: Any = None, ok: bool = True, meta: Dict = None) -> Dict:
    """Create standardized API response envelope."""
    return {"ok": ok, "meta": meta or {}, "data": data}


# Create FastAPI application
app = FastAPI(
    title="Omniverse Market API",
    description="API-first engine for prediction market data ingestion and normalization",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(markets.router, prefix="/api/v1", tags=["markets"])
app.include_router(ingest.router, prefix="/api/v1", tags=["ingestion"])


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return create_envelope(
        data={"status": "healthy", "service": "omniverse-market-api"},
        meta={"timestamp": "2024-01-01T00:00:00Z"},
    )


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler."""
    return JSONResponse(
        status_code=404,
        content=create_envelope(
            data=None, ok=False, meta={"error": "Resource not found"}
        ),
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler."""
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content=create_envelope(
            data=None, ok=False, meta={"error": "Internal server error"}
        ),
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
