import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_profile
from app.config import get_settings
from app.database import get_db
from app.models import CandidateProfile, CandidateSkill, Job, JobMatch, JobStatus, Resume, Skill, User
from app.schemas.profile import AISettingsOut, AISettingsUpdate, ProfileOut, ProfileUpdate
from app.schemas.auth import UserOut
from app.schemas.jobs import ResumeOut
from app.services.ai.env_updater import update_env_file
from app.services.ai.service import get_ai_service
from app.services.cv.extraction import ALLOWED_EXTENSIONS, CONTENT_TYPES, extract_cv_text
from app.services.matching.engine import build_candidate_dict, compute_match_scores

router = APIRouter(tags=["profile"])


def profile_to_out(profile: CandidateProfile) -> ProfileOut:
    skills = [cs.skill.name for cs in profile.skills if cs.skill]
    return ProfileOut(
        id=profile.id,
        professional_level=profile.professional_level,
        professional_summary=profile.professional_summary,
        preferred_roles=profile.preferred_roles,
        preferred_locations=profile.preferred_locations,
        employment_types=profile.employment_types,
        minimum_salary=profile.minimum_salary,
        salary_currency=profile.salary_currency,
        experience_level=profile.experience_level,
        work_authorization=profile.work_authorization,
        keywords=profile.keywords,
        search_terms=profile.search_terms,
        skills=skills,
        structured_data=profile.structured_data,
    )


async def sync_skills(db: AsyncSession, profile: CandidateProfile, skill_names: list[str]) -> None:
    await db.execute(delete(CandidateSkill).where(CandidateSkill.profile_id == profile.id))
    await db.flush()

    seen_skills = set()
    for name in skill_names:
        n = name.strip()
        if not n:
            continue
        key = n.lower()
        if key in seen_skills:
            continue
        seen_skills.add(key)

        result = await db.execute(select(Skill).where(Skill.name.ilike(n)))
        skill = result.scalar_one_or_none()
        if not skill:
            skill = Skill(name=n)
            db.add(skill)
            await db.flush()

        db.add(CandidateSkill(profile_id=profile.id, skill_id=skill.id))
    await db.flush()


async def sync_profile_and_matches_for_resume(db: AsyncSession, user: User, resume: Resume) -> CandidateProfile:
    profile = await get_profile(db, user)
    analysis = resume.analysis_json or {}

    # 1. Reset profile summary and seniority strictly to THIS resume
    profile.professional_summary = analysis.get("professional_summary") or profile.professional_summary
    profile.experience_level = analysis.get("seniority_level") or profile.experience_level
    profile.structured_data = analysis

    # 2. Reset roles strictly to THIS resume
    roles = analysis.get("potential_job_titles") or []
    profile.preferred_roles = roles

    # 3. Reset search_terms strictly to THIS resume
    profile.search_terms = roles[:6] if roles else ["software developer"]

    # 4. Reset keywords strictly to THIS resume
    kw = list(analysis.get("skills") or [])
    kw.extend(analysis.get("tools") or [])
    profile.keywords = list(dict.fromkeys(kw))[:10]

    # 5. Reset candidate skills strictly to THIS resume
    skill_names = list(analysis.get("skills") or [])
    skill_names.extend(analysis.get("programming_languages") or [])
    await sync_skills(db, profile, skill_names)
    await db.flush()

    # 6. Delete old JobMatches for THIS resume so we rebuild with the updated profile
    await db.execute(delete(JobMatch).where(JobMatch.user_id == user.id, JobMatch.resume_id == resume.id))
    await db.flush()

    # 7. Re-evaluate existing jobs against this active CV's candidate profile
    jobs_res = await db.execute(select(Job).limit(300))
    all_jobs = jobs_res.scalars().all()
    candidate_dict = build_candidate_dict(profile)
    settings = get_settings()
    weights = settings.match_weights()

    for job in all_jobs:
        job_analysis = job.analysis_json or {}
        scores, reasons, gaps = compute_match_scores(candidate_dict, job, job_analysis, profile)
        overall = sum(scores[k] * weights[k] for k in weights if k in scores)
        if overall >= 0.35:
            db.add(
                JobMatch(
                    user_id=user.id,
                    job_id=job.id,
                    resume_id=resume.id,
                    overall_score=round(overall * 100, 1),
                    component_scores={k: round(v * 100, 1) for k, v in scores.items()},
                    match_reasons=reasons,
                    gap_reasons=gaps,
                    status=JobStatus.NEW,
                )
            )
    await db.flush()
    return profile


@router.get("/profile", response_model=ProfileOut)
async def get_user_profile(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(db, user)
    return profile_to_out(profile)


@router.put("/profile", response_model=ProfileOut)
async def update_profile(
    payload: ProfileUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    profile = await get_profile(db, user)
    for field in payload.model_fields:
        if field == "skills":
            continue
        val = getattr(payload, field)
        if val is not None or field in {
            "preferred_roles",
            "preferred_locations",
            "employment_types",
            "keywords",
            "search_terms",
        }:
            setattr(profile, field, val)
    if payload.skills:
        await sync_skills(db, profile, payload.skills)
    await db.flush()
    profile = await get_profile(db, user)
    return profile_to_out(profile)


@router.get("/settings/ai", response_model=AISettingsOut)
async def get_ai_settings(user: User = Depends(get_current_user)):
    settings = get_settings()
    key = settings.ai_api_key.strip() if settings.ai_api_key else ""
    masked = None
    if key:
        if len(key) > 8:
            masked = f"{key[:4]}...{key[-4:]}"
        else:
            masked = "********"

    return AISettingsOut(
        ai_provider=settings.ai_provider,
        ai_base_url=settings.ai_base_url,
        ai_model=settings.ai_model,
        ai_api_key_configured=bool(key),
        ai_api_key_masked=masked,
    )


@router.put("/settings/ai", response_model=AISettingsOut)
async def update_ai_settings(
    payload: AISettingsUpdate,
    user: User = Depends(get_current_user),
):
    updates = {}
    if payload.ai_provider is not None:
        provider = payload.ai_provider.strip().lower()
        updates["AI_PROVIDER"] = provider
        if provider == "groq" and not payload.ai_base_url:
            updates["AI_BASE_URL"] = "https://api.groq.com/openai/v1"
    if payload.ai_base_url is not None:
        updates["AI_BASE_URL"] = payload.ai_base_url.strip()
    if payload.ai_model is not None:
        updates["AI_MODEL"] = payload.ai_model.strip()
    if payload.ai_api_key is not None:
        updates["AI_API_KEY"] = payload.ai_api_key.strip()

    if updates:
        update_env_file(updates)

    return await get_ai_settings(user)


@router.post("/resume/upload", response_model=ResumeOut)
async def upload_resume(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    settings = get_settings()
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file type. Use PDF, DOCX, or TXT.")

    content = await file.read()
    if len(content) > settings.max_cv_bytes:
        raise HTTPException(status_code=400, detail="File exceeds maximum size")

    user_dir = settings.upload_path / str(user.id)
    user_dir.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}{suffix}"
    stored_path = user_dir / stored_name
    stored_path.write_bytes(content)

    try:
        text = extract_cv_text(stored_path)
    except Exception as exc:
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail=f"Could not extract text: {exc}") from exc

    if not text.strip():
        stored_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="No text found in CV")

    result = await db.execute(select(Resume).where(Resume.user_id == user.id, Resume.is_active.is_(True)))
    for r in result.scalars().all():
        r.is_active = False

    ai = get_ai_service()
    try:
        analysis = await ai.analyze_cv(text)
    except Exception as exc:
        analysis = None
        analysis_error = str(exc)
    else:
        analysis_error = None

    resume = Resume(
        user_id=user.id,
        filename=file.filename or stored_name,
        stored_path=str(stored_path),
        content_type=CONTENT_TYPES.get(suffix, file.content_type or "application/octet-stream"),
        extracted_text=text,
        analysis_json=analysis,
        is_active=True,
    )
    db.add(resume)
    await db.flush()

    if analysis:
        await sync_profile_and_matches_for_resume(db, user, resume)

    await db.commit()

    out = ResumeOut(
        id=resume.id,
        filename=resume.filename,
        content_type=resume.content_type,
        is_active=resume.is_active,
        created_at=resume.created_at,
        has_analysis=analysis is not None,
        analysis=analysis,
        extracted_text=resume.extracted_text[:1000] if resume.extracted_text else None,
    )
    if analysis_error and not analysis:
        out.has_analysis = False
    return out


@router.post("/resume/{resume_id}/activate", response_model=ResumeOut)
async def activate_resume(
    resume_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Resume).where(Resume.user_id == user.id))
    resumes = result.scalars().all()
    target_resume = None
    for r in resumes:
        if r.id == resume_id:
            r.is_active = True
            target_resume = r
        else:
            r.is_active = False

    if not target_resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    await sync_profile_and_matches_for_resume(db, user, target_resume)
    await db.commit()

    return ResumeOut(
        id=target_resume.id,
        filename=target_resume.filename,
        content_type=target_resume.content_type,
        is_active=target_resume.is_active,
        created_at=target_resume.created_at,
        has_analysis=bool(target_resume.analysis_json),
        analysis=target_resume.analysis_json,
        extracted_text=target_resume.extracted_text[:1000] if target_resume.extracted_text else None,
    )


@router.get("/resume", response_model=list[ResumeOut])
async def list_resumes(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.user_id == user.id).order_by(Resume.created_at.desc()))
    resumes = result.scalars().all()
    return [
        ResumeOut(
            id=r.id,
            filename=r.filename,
            content_type=r.content_type,
            is_active=r.is_active,
            created_at=r.created_at,
            has_analysis=bool(r.analysis_json),
            analysis=r.analysis_json,
            extracted_text=r.extracted_text[:1000] if r.extracted_text else None,
        )
        for r in resumes
    ]


@router.post("/resume/{resume_id}/analyze", response_model=ResumeOut)
async def analyze_resume(
    resume_id: int,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == user.id)
    )
    resume = result.scalar_one_or_none()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    ai = get_ai_service()
    text = resume.extracted_text or ""
    try:
        analysis = await ai.analyze_cv(text)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"AI Analysis failed: {exc}") from exc

    resume.analysis_json = analysis
    await db.flush()

    if resume.is_active:
        await sync_profile_and_matches_for_resume(db, user, resume)

    await db.commit()

    return ResumeOut(
        id=resume.id,
        filename=resume.filename,
        content_type=resume.content_type,
        is_active=resume.is_active,
        created_at=resume.created_at,
        has_analysis=bool(resume.analysis_json),
        analysis=resume.analysis_json,
        extracted_text=resume.extracted_text[:1000] if resume.extracted_text else None,
    )


@router.delete("/resume")
async def delete_resume(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Resume).where(Resume.user_id == user.id))
    for resume in result.scalars().all():
        Path(resume.stored_path).unlink(missing_ok=True)
        await db.delete(resume)
    return {"message": "CV deleted"}
