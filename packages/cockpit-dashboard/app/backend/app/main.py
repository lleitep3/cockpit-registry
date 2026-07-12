from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import setup_logging
from app.routers import cockpit, health, kb, logs, mini_apps, overview, packages, vault


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="API do dashboard visual do AICockpit",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, tags=["health"])
app.include_router(cockpit.router, prefix="/api/v1")
app.include_router(kb.router, prefix="/api/v1")
app.include_router(logs.router, prefix="/api/v1")
app.include_router(mini_apps.router, prefix="/api/v1")
app.include_router(overview.router, prefix="/api/v1")
app.include_router(packages.router, prefix="/api/v1")
app.include_router(vault.router, prefix="/api/v1")
