"""DeepScribe AI - FastAPI Backend Application."""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import execution_router, projects_router, websocket_router
from app.core import get_settings, init_db, setup_logging

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup and shutdown."""
    # Startup
    setup_logging(debug=settings.debug)
    await init_db()
    yield
    # Shutdown
    pass


app = FastAPI(
    title="DeepScribe AI",
    description="Autonomous Agentic Blogging Platform with CrewAI + Groq",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(projects_router, prefix="/api")
app.include_router(execution_router, prefix="/api")
app.include_router(websocket_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "DeepScribe AI",
        "version": "0.1.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
