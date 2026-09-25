import asyncio
import httpx
import feedparser
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

async def safe_test(name, func):
    print(f"\n>>> Running test: {name} <<<")
    try:
        await func()
    except Exception as e:
        print(f"FAILED {name}: {e}")

async def test_brightermonday():
    url = "https://www.brightermonday.co.ke/jobs"
    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        found = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/job/" in href or "/listings/" in href:
                found += 1
                if found <= 3:
                    print(f"BM Job: {a.get_text(strip=True)} -> {href}")
        print(f"BrighterMonday total job links: {found}")

async def test_myjobmag():
    url = "https://www.myjobmag.co.ke/jobs"
    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        found = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/job/" in href and not href.endswith("/job/"):
                found += 1
                if found <= 3:
                    title = a.get_text(strip=True)
                    print(f"MyJobMag Job: {title} -> https://www.myjobmag.co.ke{href}")
        print(f"MyJobMag total job links: {found}")

async def test_careerpoint():
    url = "https://www.careerpointkenya.co.ke/"
    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        found = 0
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "job" in href or "vacancy" in href or "2024" in href or "2025" in href or "2026" in href:
                text = a.get_text(strip=True)
                if len(text) > 15:
                    found += 1
                    if found <= 3:
                        print(f"CareerPoint Job: {text} -> {href}")
        print(f"CareerPoint total job links: {found}")

async def test_jobwebkenya():
    url = "https://jobwebkenya.com/feed/"
    parsed = feedparser.parse(url)
    print(f"JobWebKenya RSS entries: {len(parsed.entries)}")
    for e in parsed.entries[:3]:
        print(f"JobWebKenya Job: {e.get('title')} -> {e.get('link')}")

async def test_workable_cloudfactory():
    url = "https://apply.workable.com/api/v1/widget/accounts/cloudfactory"
    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        print(f"CloudFactory Workable API status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            jobs = data.get("jobs", [])
            print("Jobs count:", len(jobs))
            for j in jobs[:3]:
                print("CloudFactory job:", j.get("title"), "| URL:", j.get("shortlink") or j.get("url"))

async def test_greenhouse_boards():
    boards = ["outlier", "outlierai", "cloudfactory", "turing", "rws", "welocalize", "oneforma", "lemon", "arc"]
    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
        for b in boards:
            url = f"https://boards-api.greenhouse.io/v1/boards/{b}/jobs"
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    jobs = data.get('jobs', [])
                    print(f"Greenhouse '{b}': {len(jobs)} jobs found!")
                    if jobs:
                        print(f"  Sample: {jobs[0].get('title')} -> {jobs[0].get('absolute_url')}")
            except Exception:
                pass

async def test_lever_postings():
    companies = ["welocalize", "rws", "turing", "outlier", "mindrift", "contra", "lemon"]
    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
        for c in companies:
            url = f"https://api.lever.co/v0/postings/{c}"
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    print(f"Lever '{c}': {len(data)} jobs found!")
                    if data:
                        print(f"  Sample: {data[0].get('text')} -> {data[0].get('hostedUrl')}")
            except Exception:
                pass

async def test_remoteok():
    url = "https://remoteok.com/api"
    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        data = resp.json()
        print(f"RemoteOK API count: {len(data)}")
        for item in data[1:4]: # index 0 is legal notice
            print("RemoteOK:", item.get("position"), "| Co:", item.get("company"), "| URL:", item.get("url"))

async def test_himalayas():
    url = "https://himalayas.app/jobs/api"
    async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
        resp = await client.get(url)
        data = resp.json()
        jobs = data.get("jobs", [])
        print(f"Himalayas jobs count: {len(jobs)}")
        for j in jobs[:3]:
            print("Himalayas:", j.get("title"), "| Co:", j.get("companyName"), "| URL:", j.get("applicationLink") or j.get("title"))

async def main():
    await safe_test("BrighterMonday", test_brightermonday)
    await safe_test("MyJobMag", test_myjobmag)
    await safe_test("CareerPoint", test_careerpoint)
    await safe_test("JobWebKenya", test_jobwebkenya)
    await safe_test("CloudFactory Workable", test_workable_cloudfactory)
    await safe_test("Greenhouse Boards", test_greenhouse_boards)
    await safe_test("Lever Postings", test_lever_postings)
    await safe_test("RemoteOK", test_remoteok)
    await safe_test("Himalayas", test_himalayas)

if __name__ == "__main__":
    asyncio.run(main())
