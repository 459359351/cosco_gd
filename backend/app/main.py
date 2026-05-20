import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import settings
from app.services.scheduler import start_scheduler, stop_scheduler
from app.ws.pubsub import start_pubsub_bridge
from app.ws.routes import ws_router


@asynccontextmanager
async def lifespan(_: FastAPI):
    pubsub_task = await start_pubsub_bridge()
    start_scheduler()
    try:
        yield
    finally:
        pubsub_task.cancel()
        stop_scheduler()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get("/health", tags=["system"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(api_router, prefix="/api/v1")
    app.include_router(ws_router)
    return app


app = create_app()
