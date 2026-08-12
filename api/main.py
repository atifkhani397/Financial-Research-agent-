"""
ARA-1 FastAPI Server Main Application (Day 16)
Thin orchestration service exposing REST and WebSocket endpoints for ARA-1.
"""

import sys
import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from api.routes import (
    research_router,
    challenges_router,
    tools_router,
    memory_router,
    evaluation_router,
    traces_router,
)
from api.websocket import router as ws_router

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("ara1.api.main")

app = FastAPI(
    title="ARA-1 Financial Agent API",
    description="Thin orchestration REST & WebSocket service exposing ARA-1 autonomous financial research capabilities.",
    version="1.0.0"
)

# Configure CORS for Vite frontend dev server (default http://localhost:5173) & production builds
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "*"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
app.include_router(research_router)
app.include_router(challenges_router)
app.include_router(tools_router)
app.include_router(memory_router)
app.include_router(evaluation_router)
app.include_router(traces_router)
app.include_router(ws_router)


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint confirming API service operational status."""
    return {
        "status": "ok",
        "agent": "ARA-1 Autonomous Financial Research Agent",
        "version": "1.0.0",
        "environment": "production"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)
