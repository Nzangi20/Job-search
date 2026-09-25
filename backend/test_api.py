"""Test API: login, verify matches by-resume, verify matches flat."""
import httpx
import json

BASE = "http://localhost:8000/api"

# 1. Login
r = httpx.post(f"{BASE}/auth/login", json={"email": "admin@aijobhunter.local", "password": "AdminPass123!"})
if r.status_code != 200:
    print(f"Login failed: {r.text}")
    exit(1)
token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Logged in as admin@aijobhunter.local")

# 2. Check matches by-resume
r = httpx.get(f"{BASE}/matches/by-resume", headers=headers)
groups = r.json()
print(f"\n📊 Matches By Resume: {len(groups)} group(s)")
for g in groups:
    print(f"  📄 {g['resume_filename']} (resume_id={g['resume_id']}, active={g['is_active']})")
    print(f"     {g['match_count']} matches")
    if g['matches']:
        top = g['matches'][:3]
        for m in top:
            print(f"     → {m['overall_score']:.0f}% | {m['job']['title']} @ {m['job']['company']}")

# 3. Check flat matches
r = httpx.get(f"{BASE}/matches", headers=headers)
flat = r.json()
print(f"\n📋 All Flat Matches: {len(flat)} total")
if flat:
    for m in flat[:5]:
        print(f"  {m['overall_score']:.0f}% | {m['job']['title']} @ {m['job']['company']} (resume_id={m.get('resume_id')}, resume_file={m.get('resume_filename')})")

# 4. Check resumes
r = httpx.get(f"{BASE}/resume", headers=headers)
resumes = r.json()
print(f"\n📝 Resumes: {len(resumes)} uploaded")
for rv in resumes:
    print(f"  id={rv['id']}, filename={rv['filename']}, active={rv['is_active']}, has_analysis={rv['has_analysis']}")

print("\n✅ API verification complete!")
