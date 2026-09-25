"""Link existing matches (with NULL resume_id) to the user's active resume."""
import sqlite3

conn = sqlite3.connect('ai_job_hunter.db')

# Get all users with resumes
cursor = conn.execute("""
    SELECT u.id, u.email, r.id as resume_id, r.filename 
    FROM users u 
    JOIN resumes r ON r.user_id = u.id AND r.is_active = 1
""")
users_with_resumes = cursor.fetchall()

for user_id, email, resume_id, filename in users_with_resumes:
    # Count unlinked matches
    cursor = conn.execute(
        "SELECT COUNT(*) FROM job_matches WHERE user_id = ? AND resume_id IS NULL",
        (user_id,)
    )
    unlinked = cursor.fetchone()[0]
    
    if unlinked > 0:
        conn.execute(
            "UPDATE job_matches SET resume_id = ? WHERE user_id = ? AND resume_id IS NULL",
            (resume_id, user_id)
        )
        print(f"Linked {unlinked} matches for {email} to resume '{filename}' (id={resume_id})")

conn.commit()

# Verify
cursor = conn.execute("""
    SELECT user_id, resume_id, COUNT(*) as cnt 
    FROM job_matches 
    GROUP BY user_id, resume_id
""")
print("\nMatches summary after linking:")
for row in cursor.fetchall():
    print(f"  user_id={row[0]}, resume_id={row[1]}, count={row[2]}")

conn.close()
