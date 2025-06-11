"""
Universal Data Loader API Server
Main FastAPI application with clean architecture
"""

import os
from fastapi import FastAPI
import uvicorn

from app.api.routes import health, documents, batch

# Initialize FastAPI app
app = FastAPI(
    title="Universal Data Loader API",
    description="Containerized document processing service for LLM applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include routers
app.include_router(health.router, tags=["Health"])
app.include_router(documents.router, prefix="/process", tags=["Documents"])
app.include_router(batch.router, prefix="/process", tags=["Batch"])

# Legacy endpoints for backward compatibility
app.include_router(documents.router, prefix="/jobs", tags=["Jobs"])
app.include_router(documents.router, prefix="/download", tags=["Download"])


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=False,
        access_log=True
    )