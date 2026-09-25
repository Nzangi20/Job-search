from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import CandidateProfile, CandidateSkill, JobMatch, Notification, NotificationSettings, User
from app.services.jobs.search import run_job_search_all_resumes
from app.services.notifications.email import send_email


async def scheduled_search_for_user(user_id: int) -> None:
    async with AsyncSessionLocal() as db:
        try:
            result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
            user = result.scalar_one_or_none()
            if not user:
                return
            profile_result = await db.execute(
                select(CandidateProfile)
                .where(CandidateProfile.user_id == user_id)
                .options(selectinload(CandidateProfile.skills).selectinload(CandidateSkill.skill))
            )
            profile = profile_result.scalar_one_or_none()
            if not profile:
                return
            before = await db.execute(
                select(JobMatch).where(JobMatch.user_id == user_id).options(selectinload(JobMatch.job))
            )
            before_ids = {m.id for m in before.scalars().all()}
            await run_job_search_all_resumes(db, user_id, profile, None)
            after = await db.execute(
                select(JobMatch)
                .where(JobMatch.user_id == user_id)
                .options(selectinload(JobMatch.job))
            )
            new_matches = [m for m in after.scalars().all() if m.id not in before_ids]
            if new_matches:
                top = sorted(new_matches, key=lambda m: m.overall_score, reverse=True)[:3]
                lines = [f"{m.overall_score:.0f}% — {m.job.title}" for m in top if m.job]
                body = (
                    "AI Job Hunter\n\n"
                    f"{len(new_matches)} new jobs matched your profile.\n\n"
                    "Top matches:\n\n"
                    + "\n".join(lines)
                    + "\n\nView your matches in the dashboard."
                )
                db.add(
                    Notification(
                        user_id=user_id,
                        title=f"{len(new_matches)} new job matches",
                        body=body,
                    )
                )
                settings_result = await db.execute(
                    select(NotificationSettings).where(NotificationSettings.user_id == user_id)
                )
                ns = settings_result.scalar_one_or_none()
                if ns and ns.email_enabled:
                    await send_email(user.email, "New job matches — AI Job Hunter", body)
            await db.commit()
        except Exception:
            await db.rollback()
            raise


async def run_all_scheduled_searches() -> None:
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.is_active.is_(True)))
        user_ids = [u.id for u in result.scalars().all()]
        await db.commit()
    for uid in user_ids:
        await scheduled_search_for_user(uid)
