"""Migration script: Update JobMatch unique constraint from (user_id, job_id) to (user_id, job_id, resume_id).

SQLite doesn't support ALTER TABLE DROP CONSTRAINT, so we:
1. Rename the old table
2. Create the new table with the updated constraint
3. Copy data (handle case where resume_id column may not exist)
4. Drop the old table
"""
import asyncio
from sqlalchemy import text
from app.database import engine


async def migrate():
    async with engine.begin() as conn:
        # Check if migration is needed
        result = await conn.execute(text(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='job_matches'"
        ))
        row = result.fetchone()
        if not row:
            print("No job_matches table found — it will be created on next app start.")
            return
        
        table_sql = row[0] or ""
        if "uq_user_job_resume_match" in table_sql:
            print("Migration already applied — constraint uq_user_job_resume_match exists.")
            return

        print("Starting migration: updating job_matches unique constraint...")

        # Check if old table has resume_id column
        has_resume_id = "resume_id" in table_sql

        # 1. Rename old table
        await conn.execute(text("ALTER TABLE job_matches RENAME TO _job_matches_old"))

        # 2. Create new table with updated constraint
        await conn.execute(text("""
            CREATE TABLE job_matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
                resume_id INTEGER REFERENCES resumes(id) ON DELETE SET NULL,
                overall_score FLOAT NOT NULL,
                component_scores JSON,
                match_reasons JSON,
                gap_reasons JSON,
                status VARCHAR(10) DEFAULT 'new',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                CONSTRAINT uq_user_job_resume_match UNIQUE (user_id, job_id, resume_id)
            )
        """))

        # Create indexes
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_matches_user_id ON job_matches (user_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_matches_job_id ON job_matches (job_id)"))
        await conn.execute(text("CREATE INDEX IF NOT EXISTS ix_job_matches_resume_id ON job_matches (resume_id)"))

        # 3. Copy data from old table
        if has_resume_id:
            await conn.execute(text("""
                INSERT INTO job_matches (id, user_id, job_id, resume_id, overall_score, component_scores, match_reasons, gap_reasons, status, created_at, updated_at)
                SELECT id, user_id, job_id, resume_id, overall_score, component_scores, match_reasons, gap_reasons, status, created_at, updated_at
                FROM _job_matches_old
            """))
        else:
            await conn.execute(text("""
                INSERT INTO job_matches (id, user_id, job_id, resume_id, overall_score, component_scores, match_reasons, gap_reasons, status, created_at, updated_at)
                SELECT id, user_id, job_id, NULL, overall_score, component_scores, match_reasons, gap_reasons, status, created_at, updated_at
                FROM _job_matches_old
            """))

        # 4. Drop old table
        await conn.execute(text("DROP TABLE _job_matches_old"))

        print("Migration complete! job_matches now has unique constraint on (user_id, job_id, resume_id)")


if __name__ == "__main__":
    asyncio.run(migrate())
