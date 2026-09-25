from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_admin
from app.config import get_settings
from app.database import get_db
from app.models import Job, JobMatch, JobSource, SystemLog, User

router = APIRouter(prefix="/admin", tags=["admin"])


class JobSourceIn(BaseModel):
    name: str
    source_type: str
    config: dict = {}
    enabled: bool = True


class WeightsUpdate(BaseModel):
    skills: float | None = None
    experience: float | None = None
    role: float | None = None
    location: float | None = None
    education: float | None = None
    technology: float | None = None
    preference: float | None = None


@router.get("/stats")
async def admin_stats(_: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    users = await db.scalar(select(func.count()).select_from(User))
    jobs = await db.scalar(select(func.count()).select_from(Job))
    matches = await db.scalar(select(func.count()).select_from(JobMatch))
    sources = await db.scalar(select(func.count()).select_from(JobSource).where(JobSource.enabled.is_(True)))
    errors = await db.scalar(
        select(func.count()).select_from(JobSource).where(JobSource.last_error.isnot(None))
    )
    return {
        "users": users,
        "jobs_collected": jobs,
        "jobs_matched": matches,
        "active_sources": sources,
        "search_errors": errors,
    }


@router.get("/users")
async def list_users(_: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).order_by(User.created_at.desc()).limit(200))
    return [
        {"id": u.id, "email": u.email, "full_name": u.full_name, "role": u.role.value, "active": u.is_active}
        for u in result.scalars().all()
    ]


@router.get("/job-sources")
async def list_sources(_: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobSource))
    return [
        {
            "id": s.id,
            "name": s.name,
            "source_type": s.source_type,
            "enabled": s.enabled,
            "config": s.config,
            "last_error": s.last_error,
        }
        for s in result.scalars().all()
    ]


@router.post("/job-sources")
async def create_source(
    payload: JobSourceIn, _: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)
):
    src = JobSource(
        name=payload.name,
        source_type=payload.source_type,
        config=payload.config,
        enabled=payload.enabled,
    )
    db.add(src)
    await db.flush()
    return {"id": src.id}


@router.put("/job-sources/{source_id}/toggle")
async def toggle_source(source_id: int, _: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobSource).where(JobSource.id == source_id))
    src = result.scalar_one_or_none()
    if not src:
        return {"error": "Not found"}
    src.enabled = not src.enabled
    return {"enabled": src.enabled}


@router.get("/weights")
async def get_weights(_: User = Depends(get_current_admin)):
    return get_settings().match_weights()


@router.get("/logs")
async def logs(_: User = Depends(get_current_admin), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SystemLog).order_by(SystemLog.created_at.desc()).limit(100))
    return [{"level": l.level, "message": l.message, "created_at": l.created_at} for l in result.scalars().all()]
