from contextlib import asynccontextmanager

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import admin, auth, jobs, profile
from app.config import get_settings
from app.database import init_db
from app.seed import seed_defaults
from app.services.scheduler import run_all_scheduled_searches

scheduler = AsyncIOScheduler()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Clear cached settings so .env changes (e.g. AI model) take effect
    get_settings.cache_clear()
    await init_db()
    await seed_defaults()
    settings = get_settings()
    scheduler.add_job(
        run_all_scheduled_searches,
        "interval",
        hours=settings.default_search_interval_hours,
        id="job_search",
        replace_existing=True,
    )
    scheduler.start()
    yield
    scheduler.shutdown()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    raw_origins = [settings.frontend_url, "http://localhost:5173", "http://127.0.0.1:5173"]
    allowed_origins = []
    for o in raw_origins:
        if not o:
            continue
        for part in o.split(","):
            cleaned = part.strip().rstrip("/")
            if cleaned and cleaned not in allowed_origins:
                allowed_origins.append(cleaned)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if allowed_origins else ["*"],
        allow_origin_regex=r"https://.*\.vercel\.app|http://localhost:\d+|http://127\.0\.0\.1:\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth.router, prefix="/api")
    app.include_router(profile.router, prefix="/api")
    app.include_router(jobs.router, prefix="/api")
    app.include_router(admin.router, prefix="/api")

    @app.get("/")
    @app.get("/api/health")
    async def health():
        return {"status": "ok", "app": settings.app_name}

    return app


app = create_app()
