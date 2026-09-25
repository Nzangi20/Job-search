"""Fix: copy data from old table (which has no resume_id) into the new table, then drop old."""
import sqlite3

conn = sqlite3.connect('ai_job_hunter.db')

# Copy data from old table (no resume_id column) into new table
conn.execute("""
    INSERT INTO job_matches (id, user_id, job_id, resume_id, overall_score, component_scores, match_reasons, gap_reasons, status, created_at, updated_at)
    SELECT id, user_id, job_id, NULL, overall_score, component_scores, match_reasons, gap_reasons, status, created_at, updated_at
    FROM _job_matches_old
""")

# Drop old table
conn.execute("DROP TABLE _job_matches_old")

conn.commit()
print("Migration complete! Data copied and old table dropped.")

# Verify
cursor = conn.execute("SELECT COUNT(*) FROM job_matches")
print(f"job_matches now has {cursor.fetchone()[0]} rows")

cursor2 = conn.execute("SELECT sql FROM sqlite_master WHERE name='job_matches'")
print("Table schema:", cursor2.fetchone()[0])

conn.close()
