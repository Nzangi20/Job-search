import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from app.config import get_settings
from app.job_sources.base import NormalizedJob, normalize_url
from app.job_sources.sources import (
    ArcDevJobSource,
    BrighterMondayJobSource,
    CareerPointKenyaJobSource,
    CloudFactoryJobSource,
    ContraJobSource,
    FuzuJobSource,
    HimalayasAPIJobSource,
    JobWebKenyaJobSource,
    JobicyAPIJobSource,
    LemonIoJobSource,
    MindriftAIJobSource,
    MyJobMagKenyaJobSource,
    OneFormaJobSource,
    OutlierAIJobSource,
    RWSJobSource,
    RSSJobSource,
    RemoteCoJobSource,
    RemoteOKAPIJobSource,
    RemotiveAPIJobSource,
    TelusDigitalAIJobSource,
    TuringJobSource,
    WeWorkRemotelyRSSJobSource,
    WelocalizeJobSource,
    WellfoundJobSource,
)
from app.models import CandidateProfile, Job, JobMatch, JobSkill, JobSource, JobStatus, Search, Skill
from app.services.ai.service import get_ai_service
from app.services.jobs.dedup import content_hash, is_duplicate
from app.services.matching.engine import build_candidate_dict, compute_match_scores


async def get_enabled_sources(db: AsyncSession) -> list:
    result = await db.execute(select(JobSource).where(JobSource.enabled.is_(True)))
    db_sources = result.scalars().all()
    runtime = []

    SOURCE_MAP = {
        "remotive": RemotiveAPIJobSource,
        "jobicy": JobicyAPIJobSource,
        "weworkremotely": WeWorkRemotelyRSSJobSource,
        "brightermonday": BrighterMondayJobSource,
        "fuzu": FuzuJobSource,
        "myjobmag": MyJobMagKenyaJobSource,
        "careerpoint": CareerPointKenyaJobSource,
        "jobwebkenya": JobWebKenyaJobSource,
        "remoteok": RemoteOKAPIJobSource,
        "remoteco": RemoteCoJobSource,
        "wellfound": WellfoundJobSource,
        "himalayas": HimalayasAPIJobSource,
        "telusdigital": TelusDigitalAIJobSource,
        "rws": RWSJobSource,
        "outlier": OutlierAIJobSource,
        "mindrift": MindriftAIJobSource,
        "welocalize": WelocalizeJobSource,
        "cloudfactory": CloudFactoryJobSource,
        "oneforma": OneFormaJobSource,
        "contra": ContraJobSource,
        "lemon": LemonIoJobSource,
        "arc": ArcDevJobSource,
        "turing": TuringJobSource,
    }

    for src in db_sources:
        cfg = src.config or {}
        stype = (src.source_type or "").lower()
        name_clean = src.name.lower().replace(" ", "").replace(".", "").replace("-", "")

        if stype == "rss" and cfg.get("feed_url"):
            runtime.append(RSSJobSource(src.name, cfg["feed_url"]))
        elif stype in SOURCE_MAP:
            cls = SOURCE_MAP[stype]
            runtime.append(cls())
        elif name_clean in SOURCE_MAP:
            cls = SOURCE_MAP[name_clean]
            runtime.append(cls())
        else:
            matched_cls = None
            for k, cls in SOURCE_MAP.items():
                if k in name_clean:
                    matched_cls = cls
                    break
            if matched_cls:
                runtime.append(matched_cls())

    if not runtime:
        runtime = [
            RemotiveAPIJobSource(),
            JobicyAPIJobSource(),
            WeWorkRemotelyRSSJobSource(),
            BrighterMondayJobSource(),
            FuzuJobSource(),
            MyJobMagKenyaJobSource(),
            CareerPointKenyaJobSource(),
            JobWebKenyaJobSource(),
            RemoteOKAPIJobSource(),
            RemoteCoJobSource(),
            WellfoundJobSource(),
            HimalayasAPIJobSource(),
            CloudFactoryJobSource(),
            TuringJobSource(),
            OutlierAIJobSource(),
            TelusDigitalAIJobSource(),
            RWSJobSource(),
            MindriftAIJobSource(),
            WelocalizeJobSource(),
            OneFormaJobSource(),
            ContraJobSource(),
            LemonIoJobSource(),
            ArcDevJobSource(),
        ]
    return runtime



async def upsert_skill(db: AsyncSession, name: str) -> Skill | None:
    n = name.strip()
    if not n:
        return None
    result = await db.execute(select(Skill).where(Skill.name.ilike(n)))
    skill = result.scalar_one_or_none()
    if not skill:
        for obj in db.new:
            if isinstance(obj, Skill) and obj.name.lower() == n.lower():
                return obj
        skill = Skill(name=n)
        db.add(skill)
        await db.flush()
    return skill


async def persist_job(db: AsyncSession, normalized: NormalizedJob) -> Job | None:
    if not normalized.source_url:
        return None
    norm_url = normalize_url(normalized.source_url)
    job = Job(
        title=normalized.title,
        company=normalized.company,
        description=normalized.description,
        location=normalized.location,
        remote=normalized.remote,
        employment_type=normalized.employment_type,
        salary_min=normalized.salary_min,
        salary_max=normalized.salary_max,
        currency=normalized.currency,
        experience_required=normalized.experience_required,
        education_required=normalized.education_required,
        source=normalized.source,
        source_url=normalized.source_url,
        source_url_normalized=norm_url,
        posted_at=normalized.posted_at,
        deadline=normalized.deadline,
        content_hash=content_hash(normalized.title, normalized.company, normalized.description),
    )
    if await is_duplicate(db, job, norm_url):
        return None
    db.add(job)
    await db.flush()
    added_skill_ids = set()
    for skill_name in normalized.skills:
        if not skill_name:
            continue
        skill = await upsert_skill(db, skill_name)
        if skill and skill.id and skill.id not in added_skill_ids:
            added_skill_ids.add(skill.id)
            db.add(JobSkill(job_id=job.id, skill_id=skill.id, is_required=False))
    return job


async def analyze_job_if_needed(db: AsyncSession, job: Job) -> dict:
    if job.analysis_json:
        return job.analysis_json
    ai = get_ai_service()
    try:
        logger.info("AI analyzing job: %s at %s", job.title, job.company)
        analysis = await ai.analyze_job(job.description)
        logger.info("AI analysis complete for: %s — skills found: %s", job.title, analysis.get('required_skills', []))
        job.analysis_json = analysis
        required = analysis.get("required_skills") or []
        preferred = analysis.get("preferred_skills") or []
        added_skill_ids = set()
        for s in required:
            skill = await upsert_skill(db, s)
            if skill and skill.id and skill.id not in added_skill_ids:
                added_skill_ids.add(skill.id)
                db.add(JobSkill(job_id=job.id, skill_id=skill.id, is_required=True))
        for s in preferred:
            skill = await upsert_skill(db, s)
            if skill and skill.id and skill.id not in added_skill_ids:
                added_skill_ids.add(skill.id)
                db.add(JobSkill(job_id=job.id, skill_id=skill.id, is_required=False))
        await db.flush()
        return analysis
    except Exception as exc:
        logger.error("AI analysis failed for job '%s': %s", job.title, exc)
        await db.rollback()
        return {}


async def match_job_for_user(
    db: AsyncSession, user_id: int, profile: CandidateProfile, job: Job, analysis: dict,
    resume_id: int | None = None,
) -> JobMatch | None:
    candidate = build_candidate_dict(profile)
    scores, reasons, gaps = compute_match_scores(candidate, job, analysis, profile)
    settings = get_settings()
    weights = settings.match_weights()
    overall = sum(scores[k] * weights[k] for k in weights)

    ai = get_ai_service()
    try:
        logger.info("AI matching job '%s' for user %s (resume_id=%s)", job.title, user_id, resume_id)
        ai_match = await ai.calculate_match(candidate, analysis)
        for r in ai_match.get("match_highlights") or []:
            if r not in reasons:
                reasons.append(r)
        for g in ai_match.get("gap_highlights") or []:
            if g not in gaps:
                gaps.append(g)
        logger.info("AI match done for '%s': overall=%.1f%%", job.title, overall * 100)
    except Exception as exc:
        logger.warning("AI matching fallback for '%s': %s", job.title, exc)

    if overall < 0.35:
        return None

    result = await db.execute(
        select(JobMatch).where(
            JobMatch.user_id == user_id,
            JobMatch.job_id == job.id,
            JobMatch.resume_id == resume_id,
        )
    )
    existing = result.scalar_one_or_none()
    if existing:
        existing.overall_score = round(overall * 100, 1)
        existing.component_scores = {k: round(v * 100, 1) for k, v in scores.items()}
        existing.match_reasons = reasons
        existing.gap_reasons = gaps
        existing.resume_id = resume_id
        return existing

    match = JobMatch(
        user_id=user_id,
        job_id=job.id,
        resume_id=resume_id,
        overall_score=round(overall * 100, 1),
        component_scores={k: round(v * 100, 1) for k, v in scores.items()},
        match_reasons=reasons,
        gap_reasons=gaps,
        status=JobStatus.NEW,
    )
    db.add(match)
    await db.flush()
    return match


def build_search_terms(profile: CandidateProfile, query: str | None = None) -> list[str]:
    terms = list(profile.search_terms or [])
    terms.extend(profile.preferred_roles or [])
    terms.extend(profile.keywords or [])
    if query:
        terms.append(query)
    seen = set()
    out = []
    for t in terms:
        key = t.strip().lower()
        if key and key not in seen:
            seen.add(key)
            out.append(t.strip())
    return out[:20] or ["software developer"]


async def run_job_search(
    db: AsyncSession, user_id: int, profile: CandidateProfile, query: str | None = None,
    resume_id: int | None = None,
) -> int:
    terms = build_search_terms(profile, query)
    sources = await get_enabled_sources(db)
    collected = 0
    logger.info("Starting job search for user %s, resume_id=%s, terms=%s", user_id, resume_id, terms[:5])
    for source in sources:
        try:
            logger.info("Fetching from source: %s", source.name)
            jobs = await source.fetch_jobs(terms)
            logger.info("Source %s returned %d candidates", source.name, len(jobs))
            for normalized in jobs:
                try:
                    job = await persist_job(db, normalized)
                    if not job:
                        continue
                    collected += 1
                    analysis = await analyze_job_if_needed(db, job)
                    await match_job_for_user(db, user_id, profile, job, analysis, resume_id=resume_id)
                    await db.commit()
                except Exception as e:
                    logger.error("Error persisting job: %s", e)
                    await db.rollback()
        except Exception as exc:
            logger.error("Source %s failed: %s", source.name, exc)
            await db.rollback()
            try:
                result = await db.execute(select(JobSource).where(JobSource.name == source.name))
                src_row = result.scalar_one_or_none()
                if src_row:
                    src_row.last_error = str(exc)[:2000]
                    await db.commit()
            except Exception:
                await db.rollback()
    primary_query = query or (terms[0] if terms else "jobs")
    try:
        db.add(Search(user_id=user_id, query=primary_query, jobs_found=collected))
        await db.commit()
    except Exception:
        await db.rollback()
    logger.info("Search complete: %d new jobs collected for user %s", collected, user_id)
    return collected


async def run_job_search_all_resumes(
    db: AsyncSession, user_id: int, profile: CandidateProfile, query: str | None = None,
) -> int:
    """Search for jobs and match them against EVERY resume the user has uploaded.

    This is the main entry point for job discovery. It:
    1. Collects jobs from all enabled sources using the active profile's search terms
    2. For each collected job, creates separate match records per resume
    3. Returns the total number of new jobs collected
    """
    from app.models import Resume
    from app.services.matching.engine import build_candidate_dict as _build

    # Fetch all user resumes
    res_result = await db.execute(
        select(Resume).where(Resume.user_id == user_id).order_by(Resume.created_at.desc())
    )
    all_resumes = res_result.scalars().all()

    # Build per-resume candidate data
    resume_profiles: list[tuple[int, dict, CandidateProfile]] = []
    for resume in all_resumes:
        analysis = resume.analysis_json or {}
        if not analysis:
            continue
        # Build a temporary profile-like dict for this resume
        # We re-use the shared profile but override structured_data per resume
        temp_profile = profile
        # Build candidate dict from the resume's own analysis
        skills = set()
        for s in analysis.get("skills", []):
            skills.add(str(s).strip().lower())
        for s in analysis.get("programming_languages", []):
            skills.add(str(s).strip().lower())
        for s in analysis.get("frameworks", []):
            skills.add(str(s).strip().lower())
        for s in analysis.get("tools", []):
            skills.add(str(s).strip().lower())
        # Also include skills from the shared profile
        if profile.skills:
            for cs in profile.skills:
                if cs.skill:
                    skills.add(cs.skill.name.strip().lower())

        candidate_dict = {
            "skills": list(skills),
            "preferred_roles": analysis.get("potential_job_titles") or profile.preferred_roles or [],
            "preferred_locations": profile.preferred_locations or [],
            "employment_types": profile.employment_types or [],
            "experience_level": analysis.get("seniority_level") or profile.experience_level,
            "education": analysis.get("education") or [],
            "programming_languages": analysis.get("programming_languages") or [],
            "frameworks": analysis.get("frameworks") or [],
            "tools": analysis.get("tools") or [],
        }
        resume_profiles.append((resume.id, candidate_dict, temp_profile))

    # If user has no analyzed resumes, fall back to single-resume search
    if not resume_profiles:
        active_resume = next((r for r in all_resumes if r.is_active), None)
        resume_id = active_resume.id if active_resume else None
        return await run_job_search(db, user_id, profile, query, resume_id=resume_id)

    # Collect jobs from all sources
    terms = build_search_terms(profile, query)
    sources = await get_enabled_sources(db)
    collected = 0
    logger.info(
        "Starting multi-resume job search for user %s, %d resumes, terms=%s",
        user_id, len(resume_profiles), terms[:5],
    )

    for source in sources:
        try:
            logger.info("Fetching from source: %s", source.name)
            jobs = await source.fetch_jobs(terms)
            logger.info("Source %s returned %d candidates", source.name, len(jobs))
            for normalized in jobs:
                try:
                    job = await persist_job(db, normalized)
                    if not job:
                        # Job already exists — still need to match it against resumes
                        # Look up the existing job by normalized URL
                        from app.job_sources.base import normalize_url as _nu
                        norm_url = _nu(normalized.source_url)
                        existing_result = await db.execute(
                            select(Job).where(Job.source_url_normalized == norm_url)
                        )
                        job = existing_result.scalar_one_or_none()
                        if not job:
                            continue
                    else:
                        collected += 1

                    analysis = await analyze_job_if_needed(db, job)

                    # Match this job against EVERY resume
                    for rid, cand_dict, prof in resume_profiles:
                        try:
                            scores, reasons, gaps = compute_match_scores(cand_dict, job, analysis, prof)
                            settings = get_settings()
                            weights = settings.match_weights()
                            overall = sum(scores[k] * weights[k] for k in weights if k in scores)

                            if overall < 0.35:
                                continue

                            # Check for existing match for this resume
                            existing_match_result = await db.execute(
                                select(JobMatch).where(
                                    JobMatch.user_id == user_id,
                                    JobMatch.job_id == job.id,
                                    JobMatch.resume_id == rid,
                                )
                            )
                            existing_match = existing_match_result.scalar_one_or_none()

                            # Try AI-enhanced matching
                            ai = get_ai_service()
                            try:
                                ai_match = await ai.calculate_match(cand_dict, analysis)
                                for r in ai_match.get("match_highlights") or []:
                                    if r not in reasons:
                                        reasons.append(r)
                                for g in ai_match.get("gap_highlights") or []:
                                    if g not in gaps:
                                        gaps.append(g)
                            except Exception:
                                pass

                            if existing_match:
                                existing_match.overall_score = round(overall * 100, 1)
                                existing_match.component_scores = {k: round(v * 100, 1) for k, v in scores.items()}
                                existing_match.match_reasons = reasons
                                existing_match.gap_reasons = gaps
                            else:
                                db.add(JobMatch(
                                    user_id=user_id,
                                    job_id=job.id,
                                    resume_id=rid,
                                    overall_score=round(overall * 100, 1),
                                    component_scores={k: round(v * 100, 1) for k, v in scores.items()},
                                    match_reasons=reasons,
                                    gap_reasons=gaps,
                                    status=JobStatus.NEW,
                                ))
                        except Exception as me:
                            logger.error("Error matching job %s for resume %s: %s", job.title, rid, me)

                    await db.commit()
                except Exception as e:
                    logger.error("Error persisting job: %s", e)
                    await db.rollback()
        except Exception as exc:
            logger.error("Source %s failed: %s", source.name, exc)
            await db.rollback()
            try:
                result = await db.execute(select(JobSource).where(JobSource.name == source.name))
                src_row = result.scalar_one_or_none()
                if src_row:
                    src_row.last_error = str(exc)[:2000]
                    await db.commit()
            except Exception:
                await db.rollback()

    primary_query = query or (terms[0] if terms else "jobs")
    try:
        db.add(Search(user_id=user_id, query=primary_query, jobs_found=collected))
        await db.commit()
    except Exception:
        await db.rollback()

    logger.info("Multi-resume search complete: %d new jobs collected for user %s", collected, user_id)
    return collected

