"""FastAPI application — NetSentinel backend."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import CORS_ORIGINS
from .db.database import init_db
from .models.loader import load_models, load_scaler
from .routers import analysis, health, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load models and scaler once at startup, then initialize the database.
    load_models()
    load_scaler()
    init_db()
    yield


app = FastAPI(
    title="NetSentinel",
    description="Network threat detection API (CICIDS2017 models)",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(predict.router, tags=["prediction"])
app.include_router(analysis.router, tags=["analysis"])
