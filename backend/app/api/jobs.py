from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_user, get_profile
from app.database import get_db
from app.models import Application, Job, JobMatch, JobSkill, JobStatus, Notification, Resume, SavedJob, Search, User
from app.schemas.jobs import (
    ApplicationCreate,
    ApplicationOut,
    ApplicationQuestionRequest,
    ApplicationUpdate,
    CoverLetterRequest,
    JobMatchOut,
    JobOut,
    JobQuestionRequest,
    JobSearchRequest,
    NotificationSettingsUpdate,
    SearchOut,
)
from app.services.ai.service import get_ai_service
from app.services.jobs.search import run_job_search, run_job_search_all_resumes

router = APIRouter(tags=["jobs"])


def job_to_out(job: Job) -> JobOut:
    skills = [js.skill.name for js in job.skills if js.skill] if job.skills else []
    return JobOut(
        id=job.id,
        title=job.title,
        company=job.company,
        description=job.description,
        location=job.location,
        remote=job.remote,
        employment_type=job.employment_type,
        salary_min=job.salary_min,
        salary_max=job.salary_max,
        currency=job.currency,
        experience_required=job.experience_required,
        education_required=job.education_required,
        source=job.source,
        source_url=job.source_url,
        posted_at=job.posted_at,
        deadline=job.deadline,
        skills=skills,
        analysis=job.analysis_json,
    )


def match_to_out(match: JobMatch, resume_filename: str | None = None) -> JobMatchOut:
    return JobMatchOut(
        id=match.id,
        overall_score=match.overall_score,
        component_scores=match.component_scores,
        match_reasons=match.match_reasons,
        gap_reasons=match.gap_reasons,
        status=match.status.value,
        job=job_to_out(match.job),
        resume_id=match.resume_id,
        resume_filename=resume_filename,
    )


@router.get("/jobs", response_model=list[JobOut])
async def list_jobs(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = Query(50, le=200),
):
    result = await db.execute(
        select(Job).options(selectinload(Job.skills).selectinload(JobSkill.skill)).limit(limit)
    )
    return [job_to_out(j) for j in result.scalars().all()]


@router.get("/jobs/{job_id}", response_model=JobOut)
async def get_job(job_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Job).where(Job.id == job_id).options(selectinload(Job.skills).selectinload(JobSkill.skill))
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job_to_out(job)


@router.get("/matches", response_model=list[JobMatchOut])
async def list_matches(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    min_match: float | None = None,
    employment_type: str | None = None,
    location: str | None = None,
    experience: str | None = None,
    salary_min: float | None = None,
    salary_max: float | None = None,
    skill: list[str] = Query(default=[]),
    status_filter: str | None = Query(default=None, alias="status"),
):
    stmt = (
        select(JobMatch)
        .where(JobMatch.user_id == user.id)
        .options(selectinload(JobMatch.job).selectinload(Job.skills).selectinload(JobSkill.skill))
        .order_by(JobMatch.overall_score.desc())
    )
    if min_match is not None:
        stmt = stmt.where(JobMatch.overall_score >= min_match)
    if status_filter:
        try:
            stmt = stmt.where(JobMatch.status == JobStatus(status_filter))
        except ValueError:
            pass
    result = await db.execute(stmt)
    matches = result.scalars().all()
    
    # Build resume filename lookup
    resume_ids = {m.resume_id for m in matches if m.resume_id}
    resume_map: dict[int, str] = {}
    if resume_ids:
        res_result = await db.execute(select(Resume).where(Resume.id.in_(resume_ids)))
        for r in res_result.scalars().all():
            resume_map[r.id] = r.filename
    
    filtered = []
    for m in matches:
        job = m.job
        if employment_type and (job.employment_type or "").lower() != employment_type.lower():
            continue
        if location:
            loc = (job.location or "").lower()
            if location.lower() == "remote" and not job.remote:
                continue
            if location.lower() != "remote" and location.lower() not in loc and not job.remote:
                continue
        if experience:
            exp = (job.experience_required or job.analysis_json or {}).get("seniority", "") if isinstance(job.analysis_json, dict) else job.experience_required or ""
            if experience.lower() not in str(exp).lower():
                continue
        if salary_min is not None and job.salary_max and job.salary_max < salary_min:
            continue
        if salary_max is not None and job.salary_min and job.salary_min > salary_max:
            continue
        if skill:
            job_skills = {js.skill.name.lower() for js in job.skills if js.skill}
            if not all(s.lower() in job_skills or s.lower() in job.description.lower() for s in skill):
                continue
        filtered.append(match_to_out(m, resume_filename=resume_map.get(m.resume_id)))
    return filtered


@router.post("/jobs/search")
async def search_jobs(
    payload: JobSearchRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(db, user)
    # Use multi-resume search to match jobs against ALL uploaded CVs
    count = await run_job_search_all_resumes(db, user.id, profile, payload.query)
    # Count how many resumes were matched
    resume_result = await db.execute(
        select(Resume).where(Resume.user_id == user.id)
    )
    resume_count = len(resume_result.scalars().all())
    return {
        "jobs_collected": count,
        "message": f"Search completed — matched against {resume_count} CV(s)",
        "resumes_matched": resume_count,
    }


@router.get("/matches/by-resume")
async def matches_by_resume(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Return all matches grouped by resume/CV filename."""
    stmt = (
        select(JobMatch)
        .where(JobMatch.user_id == user.id)
        .options(selectinload(JobMatch.job).selectinload(Job.skills).selectinload(JobSkill.skill))
        .order_by(JobMatch.overall_score.desc())
    )
    result = await db.execute(stmt)
    matches = result.scalars().all()

    # Get all resumes for this user
    res_result = await db.execute(
        select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc())
    )
    resumes = res_result.scalars().all()
    resume_map = {r.id: r.filename for r in resumes}

    # Group matches by resume
    grouped: dict[str, list] = {}
    unlinked: list = []
    for m in matches:
        out = match_to_out(m, resume_filename=resume_map.get(m.resume_id))
        if m.resume_id and m.resume_id in resume_map:
            key = resume_map[m.resume_id]
            grouped.setdefault(key, []).append(out)
        else:
            unlinked.append(out)

    result_groups = []
    for r in resumes:
        if r.filename in grouped:
            result_groups.append({
                "resume_id": r.id,
                "resume_filename": r.filename,
                "is_active": r.is_active,
                "matches": grouped[r.filename],
                "match_count": len(grouped[r.filename]),
            })
    if unlinked:
        result_groups.append({
            "resume_id": None,
            "resume_filename": "General Matches",
            "is_active": False,
            "matches": unlinked,
            "match_count": len(unlinked),
        })
    return result_groups


@router.post("/jobs/{job_id}/save")
async def save_job(job_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")
    existing = await db.execute(
        select(SavedJob).where(SavedJob.user_id == user.id, SavedJob.job_id == job_id)
    )
    if not existing.scalar_one_or_none():
        db.add(SavedJob(user_id=user.id, job_id=job_id))
    match = await db.execute(select(JobMatch).where(JobMatch.user_id == user.id, JobMatch.job_id == job_id))
    m = match.scalar_one_or_none()
    if m:
        m.status = JobStatus.SAVED
    return {"message": "Saved"}


@router.post("/jobs/{job_id}/ignore")
async def ignore_job(job_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    match = await db.execute(select(JobMatch).where(JobMatch.user_id == user.id, JobMatch.job_id == job_id))
    m = match.scalar_one_or_none()
    if m:
        m.status = JobStatus.IGNORED
    else:
        db.add(
            JobMatch(
                user_id=user.id,
                job_id=job_id,
                overall_score=0,
                status=JobStatus.IGNORED,
            )
        )
    return {"message": "Ignored"}


@router.post("/jobs/{job_id}/applied")
async def mark_applied(job_id: int, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Job).where(Job.id == job_id))
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Job not found")
    app = Application(user_id=user.id, job_id=job_id, status=JobStatus.APPLIED)
    db.add(app)
    match = await db.execute(select(JobMatch).where(JobMatch.user_id == user.id, JobMatch.job_id == job_id))
    m = match.scalar_one_or_none()
    if m:
        m.status = JobStatus.APPLIED
    return {"message": "Marked as applied"}


@router.get("/searches", response_model=list[SearchOut])
async def search_history(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Search).where(Search.user_id == user.id).order_by(Search.created_at.desc()).limit(100)
    )
    return result.scalars().all()


@router.post("/applications", response_model=ApplicationOut)
async def create_application(
    payload: ApplicationCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    status_enum = JobStatus(payload.status)
    app = Application(user_id=user.id, job_id=payload.job_id, status=status_enum, notes=payload.notes)
    db.add(app)
    await db.flush()
    job_result = await db.execute(
        select(Job).where(Job.id == payload.job_id).options(selectinload(Job.skills).selectinload(JobSkill.skill))
    )
    job = job_result.scalar_one_or_none()
    return ApplicationOut(
        id=app.id,
        job_id=app.job_id,
        status=app.status.value,
        notes=app.notes,
        job=job_to_out(job) if job else None,
    )


@router.put("/applications/{app_id}", response_model=ApplicationOut)
async def update_application(
    app_id: int,
    payload: ApplicationUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Application).where(Application.id == app_id, Application.user_id == user.id))
    app = result.scalar_one_or_none()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    if payload.status:
        app.status = JobStatus(payload.status)
    if payload.notes is not None:
        app.notes = payload.notes
    await db.flush()
    return ApplicationOut(id=app.id, job_id=app.job_id, status=app.status.value, notes=app.notes)


@router.get("/applications", response_model=list[ApplicationOut])
async def list_applications(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Application).where(Application.user_id == user.id))
    apps = result.scalars().all()
    out = []
    for app in apps:
        job_result = await db.execute(
            select(Job).where(Job.id == app.job_id).options(selectinload(Job.skills).selectinload(JobSkill.skill))
        )
        job = job_result.scalar_one_or_none()
        out.append(
            ApplicationOut(
                id=app.id,
                job_id=app.job_id,
                status=app.status.value,
                notes=app.notes,
                job=job_to_out(job) if job else None,
            )
        )
    return out


@router.get("/notifications")
async def list_notifications(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Notification).where(Notification.user_id == user.id).order_by(Notification.created_at.desc())
    )
    return [
        {"id": n.id, "title": n.title, "body": n.body, "read": n.read, "created_at": n.created_at}
        for n in result.scalars().all()
    ]


@router.put("/notifications/settings")
async def update_notification_settings(
    payload: NotificationSettingsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models import NotificationSettings

    result = await db.execute(select(NotificationSettings).where(NotificationSettings.user_id == user.id))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = NotificationSettings(user_id=user.id)
        db.add(settings)
    if payload.email_enabled is not None:
        settings.email_enabled = payload.email_enabled
    if payload.telegram_enabled is not None:
        settings.telegram_enabled = payload.telegram_enabled
    if payload.telegram_chat_id is not None:
        settings.telegram_chat_id = payload.telegram_chat_id
    return {"message": "Updated"}


@router.get("/dashboard/stats")
async def dashboard_stats(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    matches = await db.execute(select(JobMatch).where(JobMatch.user_id == user.id))
    all_m = matches.scalars().all()
    return {
        "new_matches": sum(1 for m in all_m if m.status == JobStatus.NEW),
        "high_matches": sum(1 for m in all_m if m.overall_score >= 80),
        "applied": sum(1 for m in all_m if m.status == JobStatus.APPLIED),
        "saved": sum(1 for m in all_m if m.status == JobStatus.SAVED),
        "rejected": sum(1 for m in all_m if m.status == JobStatus.REJECTED),
    }


@router.post("/application-assistant/cover-letter")
async def cover_letter(
    payload: CoverLetterRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models import Resume

    job_r = await db.execute(select(Job).where(Job.id == payload.job_id))
    job = job_r.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    resume_r = await db.execute(
        select(Resume).where(Resume.user_id == user.id, Resume.is_active.is_(True))
    )
    resume = resume_r.scalar_one_or_none()
    if not resume or not resume.extracted_text:
        raise HTTPException(status_code=400, detail="Upload a CV first")
    ai = get_ai_service()
    text = await ai.generate_cover_letter(resume.extracted_text, job.description)
    return {"cover_letter": text, "disclaimer": "Review and edit before submitting."}


@router.post("/application-assistant/answers")
async def application_answers(
    payload: ApplicationQuestionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models import Resume

    job_r = await db.execute(select(Job).where(Job.id == payload.job_id))
    job = job_r.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    resume_r = await db.execute(
        select(Resume).where(Resume.user_id == user.id, Resume.is_active.is_(True))
    )
    resume = resume_r.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=400, detail="Upload a CV first")
    ai = get_ai_service()
    answers = await ai.answer_application_question(
        resume.extracted_text or "", job.description, payload.questions
    )
    return {"answers": answers, "disclaimer": "Review and edit before submitting."}


@router.post("/application-assistant/ask")
async def ask_job_question(
    payload: JobQuestionRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    from app.models import Resume

    job_r = await db.execute(select(Job).where(Job.id == payload.job_id))
    job = job_r.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    resume_r = await db.execute(
        select(Resume).where(Resume.user_id == user.id, Resume.is_active.is_(True))
    )
    resume = resume_r.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=400, detail="Upload a CV first")
    ai = get_ai_service()
    answer = await ai.ask_job_question(
        resume.extracted_text or "", job.description, payload.question
    )
    return {
        "question": payload.question,
        "answer": answer,
        "disclaimer": "Review and edit AI-generated advice before submitting applications.",
    }

