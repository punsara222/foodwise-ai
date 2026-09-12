"""
FastAPI entrypoint for the FoodWise AI orchestrator.

Run locally with:
    uvicorn orchestrator.main:app --reload --port 8000
(run from the foodwise-ai/ project root, not from inside orchestrator/)
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .routers import health, query

app = FastAPI(
    title=settings.APP_NAME,
    description="Orchestrator for the FoodWise AI multi-agent recipe & nutrition assistant.",
    version="0.1.0",
)

# CORS is wide open for local dev so the Streamlit frontend can call this
# freely. Tighten allow_origins before any real deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(query.router)


@app.exception_handler(ConnectionError)
async def connection_error_handler(request: Request, exc: ConnectionError):
    return JSONResponse(status_code=503, content={"detail": str(exc)})


@app.exception_handler(RuntimeError)
async def runtime_error_handler(request: Request, exc: RuntimeError):
    return JSONResponse(status_code=502, content={"detail": str(exc)})


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError):
    return JSONResponse(status_code=400, content={"detail": str(exc)})
