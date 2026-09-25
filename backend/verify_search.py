import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import CandidateProfile, Job, JobMatch, User
from app.services.jobs.search import run_job_search

async def main():
    async with AsyncSessionLocal() as db:
        res = await db.execute(select(User))
        user = res.scalars().first()
        if not user:
            print("No user found")
            return
        
        profile_res = await db.execute(select(CandidateProfile).where(CandidateProfile.user_id == user.id))
        profile = profile_res.scalar_one_or_none()
        if not profile:
            profile = CandidateProfile(
                user_id=user.id,
                title="Software Engineer / AI Enthusiast",
                experience_years=3,
                skills=["Python", "JavaScript", "React", "AI", "Data"],
                search_terms=["developer", "ai", "kenya", "remote"],
                preferred_roles=["Software Engineer", "AI Evaluator"],
            )
            db.add(profile)
            await db.commit()
            await db.refresh(profile)

        print(f"Running job search across all configured sources for user {user.id}...")
        collected = await run_job_search(db, user.id, profile, query="software developer")
        print(f"Total new jobs collected & matched: {collected}")

        jobs_count = await db.execute(select(Job))
        print(f"Total jobs in database: {len(jobs_count.scalars().all())}")

if __name__ == "__main__":
    asyncio.run(main())
