import hashlib
from urllib.parse import urlparse

from rapidfuzz import fuzz
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.job_sources.base import normalize_url
from app.models import Job


def content_hash(title: str, company: str, description: str) -> str:
    raw = f"{title}|{company}|{description[:500]}".lower()
    return hashlib.sha256(raw.encode()).hexdigest()


async def is_duplicate(db: AsyncSession, job: Job, normalized_url: str) -> bool:
    by_url = await db.execute(select(Job).where(Job.source_url_normalized == normalized_url))
    if by_url.scalar_one_or_none():
        return True

    result = await db.execute(
        select(Job).where(Job.company == job.company, Job.title == job.title)
    )
    existing = result.scalars().all()
    for ex in existing:
        if fuzz.ratio(ex.description[:1000], job.description[:1000]) >= 90:
            return True
    return False


def normalize_job_url(url: str) -> str:
    if not url:
        return ""
    return normalize_url(url)
