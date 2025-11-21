#!/usr/bin/env python3
"""
FastAPI application entry point for competing LLM chat application.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from competing_llm.backend.configuration.config import config
from competing_llm.backend.routers.chat import router as chat_router
from competing_llm.backend.routers.chat_v2 import router as chat_v2_router

# Configure logging
logging.basicConfig(level=getattr(logging, config.log_level), format=config.log_format)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan management.
    """
    # Startup
    logger.info(f"Starting competing-llm API on {config.host}:{config.port}")
    yield
    # Shutdown
    logger.info("Shutting down competing-llm API")


# Create FastAPI application
app = FastAPI(
    title=config.api_title,
    description=config.api_description,
    version=config.api_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(chat_router)
app.include_router(chat_v2_router)


@app.get("/")
async def root():
    """
    Root endpoint.
    """
    return {
        "message": "Welcome to competing-llm API",
        "version": config.api_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    """
    Overall application health check.
    """
    return {"status": "healthy", "service": "competing-llm-api"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "competing_llm.backend.app:app",
        host=config.host,
        port=config.port,
        reload=config.reload,
        log_level=config.log_level.lower(),
    )
