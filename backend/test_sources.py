import asyncio
import httpx
import feedparser
from bs4 import BeautifulSoup
import json

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

async def inspect_url(name, url, method="GET", extra_headers=None):
    headers = {**HEADERS, **(extra_headers or {})}
    print(f"\n================ {name} ================")
    print(f"URL: {url}")
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True, headers=headers) as client:
            resp = await client.get(url) if method=="GET" else await client.post(url)
            print(f"Status: {resp.status_code}")
            content_type = resp.headers.get("content-type", "")
            print(f"Content-Type: {content_type}")
            
            # Check RSS
            if "xml" in content_type or "rss" in content_type or url.endswith(".xml") or url.endswith("/feed"):
                parsed = feedparser.parse(resp.text)
                print(f"RSS entries: {len(parsed.entries)}")
                if parsed.entries:
                    print(f"Sample title: {parsed.entries[0].get('title')}")
                    print(f"Sample link: {parsed.entries[0].get('link')}")
                return "rss", len(parsed.entries)

            # Check JSON
            if "json" in content_type or resp.text.strip().startswith("{") or resp.text.strip().startswith("["):
                try:
                    data = resp.json()
                    if isinstance(data, list):
                        print(f"JSON Array count: {len(data)}")
                        if data and isinstance(data[0], dict):
                            print(f"Sample keys: {list(data[0].keys())[:5]}")
                        return "json", len(data)
                    elif isinstance(data, dict):
                        print(f"JSON Dict keys: {list(data.keys())}")
                        return "json", len(data)
                except Exception:
                    pass

            # HTML Parsing
            soup = BeautifulSoup(resp.text, "html.parser")
            # Look for job links, articles, job cards
            job_links = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                text = a.get_text(strip=True)
                if text and ("job" in href or "career" in href or "vacancy" in href or "opportunity" in href or "apply" in href or "positions" in href):
                    job_links.append((text, href))
            
            print(f"Total <a> tags: {len(soup.find_all('a'))}")
            print(f"Relevant job links found: {len(job_links)}")
            if job_links:
                print("Sample links:")
                for text, href in job_links[:3]:
                    print(f"  - {text[:50]} -> {href[:80]}")
            return "html", len(job_links)

    except Exception as e:
        print(f"ERROR: {e}")
        return "error", 0

async def main():
    targets = [
        # Kenya
        ("BrighterMonday", "https://www.brightermonday.co.ke/jobs"),
        ("Fuzu Kenya", "https://www.fuzu.com/kenya/jobs"),
        ("Fuzu API/List", "https://www.fuzu.com/api/v1/jobs"),
        ("MyJobMag Kenya Jobs", "https://www.myjobmag.co.ke/jobs-in-kenya"),
        ("MyJobMag Kenya Latest", "https://www.myjobmag.co.ke/jobs"),
        ("CareerPoint Kenya RSS", "https://www.careerpointkenya.co.ke/category/job-vacancies-in-kenya/feed/"),
        ("JobWeb Kenya RSS", "https://jobwebkenya.com/feed/"),

        # Remote
        ("WeWorkRemotely RSS", "https://weworkremotely.com/remote-jobs.rss"),
        ("Remote OK API", "https://remoteok.com/api"),
        ("Remote.co Developer Jobs", "https://remote.co/remote-jobs/developer/"),
        ("Wellfound Jobs", "https://wellfound.com/jobs"),
        ("Remotive API", "https://remotive.com/api/remote-jobs"),
        ("Himalayas API", "https://himalayas.app/jobs/api"),

        # AI / Data
        ("TELUS Digital AI", "https://jobs.telusdigital.com/en_US/careers/PipelineDetail/AI-Community-Surfer-Kenya/49463"),
        ("TELUS Digital Search", "https://jobs.telusdigital.com/en_US/careers/SearchJobs"),
        ("RWS Careers", "https://www.rws.com/careers/open-positions/"),
        ("Outlier AI Careers", "https://outlier.ai/"),
        ("Mindrift AI", "https://mindrift.ai/"),
        ("Welocalize Jobs", "https://jobs.lever.co/welocalize"),
        ("CloudFactory Careers", "https://www.cloudfactory.com/careers"),
        ("OneForma Opportunities", "https://www.oneforma.com/job-opportunities/"),

        # Tech / Contract
        ("Contra Opportunities", "https://contra.com/freelance-jobs"),
        ("Lemon.io Developers", "https://lemon.io/for-developers/"),
        ("Arc Remote Jobs", "https://arc.dev/remote-jobs"),
        ("Turing Jobs", "https://www.turing.com/jobs"),
    ]

    for name, url in targets:
        await inspect_url(name, url)

if __name__ == "__main__":
    asyncio.run(main())
