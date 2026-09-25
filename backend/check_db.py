import sqlite3

conn = sqlite3.connect('ai_job_hunter.db')

# Check users
cursor = conn.execute("SELECT id, email, full_name FROM users")
print("Users:")
for row in cursor.fetchall():
    print(f"  id={row[0]}, email={row[1]}, name={row[2]}")

# Check resumes
cursor = conn.execute("SELECT id, user_id, filename, is_active, analysis_json IS NOT NULL as has_analysis FROM resumes")
print("\nResumes:")
for row in cursor.fetchall():
    print(f"  id={row[0]}, user_id={row[1]}, filename={row[2]}, active={row[3]}, has_analysis={row[4]}")

# Check matches summary
cursor = conn.execute("SELECT user_id, resume_id, COUNT(*) as cnt, AVG(overall_score) as avg_score FROM job_matches GROUP BY user_id, resume_id")
print("\nMatches by user/resume:")
for row in cursor.fetchall():
    print(f"  user_id={row[0]}, resume_id={row[1]}, count={row[2]}, avg_score={row[3]:.1f}")

# Check a few match scores
cursor = conn.execute("SELECT id, overall_score, status FROM job_matches WHERE user_id=5 ORDER BY overall_score DESC LIMIT 10")
print("\nTop 10 matches for user 5:")
for row in cursor.fetchall():
    print(f"  id={row[0]}, score={row[1]}, status={row[2]}")

conn.close()
