"""
Universal Data Loader API Server
Main FastAPI application with clean architecture
"""

import os
from fastapi import FastAPI
import uvicorn

from app.api.routes import health, jobs

# Initialize FastAPI app
app = FastAPI(
    title="Universal Data Loader API",
    description="A containerized microservice to process any document into clean, AI-ready data.",
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={
        "name": "API Support",
        "url": "https://github.com/your-repo/issues",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
)

# --- API Routers ---
# A single, clean health check endpoint.
app.include_router(health.router, tags=["Health"])

# All core functionality is consolidated under a single, versioned endpoint.
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    # Use the application's reloader in debug mode for a better development experience.
    reload = os.getenv("ENVIRONMENT") == "development"
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=reload,
        access_log=True
    )