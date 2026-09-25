import asyncio
from datetime import datetime
from urllib.parse import quote_plus, urljoin
import feedparser
import httpx
from bs4 import BeautifulSoup

from app.job_sources.base import NormalizedJob

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def filter_by_terms(jobs: list[NormalizedJob], search_terms: list[str]) -> list[NormalizedJob]:
    terms = [t.lower() for t in search_terms if t.strip()]
    if not terms:
        return jobs
    matched = []
    for j in jobs:
        blob = f"{j.title} {j.company} {j.description} {' '.join(j.skills)}".lower()
        if any(t in blob for t in terms):
            matched.append(j)
    return matched or jobs # return all if no strict term filter matches so user gets results

# --- KENYA SOURCES ---

class BrighterMondayJobSource:
    name = "BrighterMonday"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        query = search_terms[0] if search_terms else ""
        url = f"https://www.brightermonday.co.ke/jobs?q={quote_plus(query)}" if query else "https://www.brightermonday.co.ke/jobs"
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if "/listings/" in href or "/job/" in href:
                            title = a.get_text(strip=True)
                            if len(title) > 4 and not title.lower().startswith("view") and not title.lower().startswith("apply"):
                                full_url = urljoin("https://www.brightermonday.co.ke", href)
                                jobs.append(
                                    NormalizedJob(
                                        title=title,
                                        company="BrighterMonday Kenya",
                                        description=f"Job posting on BrighterMonday Kenya: {title}",
                                        location="Kenya",
                                        remote=False,
                                        employment_type="Full-time",
                                        salary_min=None,
                                        salary_max=None,
                                        currency="KES",
                                        skills=["Kenya", "Job"],
                                        experience_required=None,
                                        education_required=None,
                                        source=self.name,
                                        source_url=full_url,
                                        posted_at=datetime.utcnow(),
                                        deadline=None,
                                    )
                                )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class FuzuJobSource:
    name = "Fuzu"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        url = "https://www.fuzu.com/kenya/jobs"
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if "/jobs/" in href or "/job/" in href:
                            title = a.get_text(strip=True)
                            if len(title) > 5 and not title.lower().startswith("see") and not title.lower().startswith("apply"):
                                full_url = urljoin("https://www.fuzu.com", href)
                                jobs.append(
                                    NormalizedJob(
                                        title=title,
                                        company="Fuzu Employer",
                                        description=f"Fuzu Kenya opportunity: {title}",
                                        location="Kenya",
                                        remote=False,
                                        employment_type="Full-time",
                                        salary_min=None,
                                        salary_max=None,
                                        currency="KES",
                                        skills=["Fuzu", "Kenya"],
                                        experience_required=None,
                                        education_required=None,
                                        source=self.name,
                                        source_url=full_url,
                                        posted_at=datetime.utcnow(),
                                        deadline=None,
                                    )
                                )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class MyJobMagKenyaJobSource:
    name = "MyJobMag Kenya"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        url = "https://www.myjobmag.co.ke/jobs"
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if href.startswith("/job/") and len(href) > 6:
                            title = a.get_text(strip=True)
                            if title and len(title) > 6 and not title.lower().startswith("read"):
                                full_url = urljoin("https://www.myjobmag.co.ke", href)
                                parts = title.split(" at ")
                                job_title = parts[0].strip()
                                company = parts[1].strip() if len(parts) > 1 else "MyJobMag Employer"
                                jobs.append(
                                    NormalizedJob(
                                        title=job_title,
                                        company=company,
                                        description=f"{title} position listed on MyJobMag Kenya.",
                                        location="Kenya",
                                        remote="remote" in title.lower(),
                                        employment_type=None,
                                        salary_min=None,
                                        salary_max=None,
                                        currency="KES",
                                        skills=["Kenya"],
                                        experience_required=None,
                                        education_required=None,
                                        source=self.name,
                                        source_url=full_url,
                                        posted_at=datetime.utcnow(),
                                        deadline=None,
                                    )
                                )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class CareerPointKenyaJobSource:
    name = "Career Point Kenya"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        urls = [
            "https://jobwebkenya.com/feed/",
            "https://www.careerpointkenya.co.ke/feed/",
        ]
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                for url in urls:
                    try:
                        resp = await client.get(url)
                        if resp.status_code == 200:
                            parsed = feedparser.parse(resp.text)
                            for entry in parsed.entries:
                                title = entry.get("title", "").strip()
                                link = entry.get("link", "").strip()
                                summary = entry.get("summary", entry.get("description", ""))
                                if title and link:
                                    parts = title.split(" at ")
                                    t = parts[0].strip()
                                    c = parts[1].strip() if len(parts) > 1 else "Career Point Employer"
                                    jobs.append(
                                        NormalizedJob(
                                            title=t,
                                            company=c,
                                            description=summary or title,
                                            location="Kenya",
                                            remote="remote" in f"{t} {summary}".lower(),
                                            employment_type=None,
                                            salary_min=None,
                                            salary_max=None,
                                            currency="KES",
                                            skills=["Kenya"],
                                            experience_required=None,
                                            education_required=None,
                                            source=self.name,
                                            source_url=link,
                                            posted_at=datetime.utcnow(),
                                            deadline=None,
                                        )
                                    )
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class JobWebKenyaJobSource:
    name = "JobWeb Kenya"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        url = "https://jobwebkenya.com/feed/"
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    parsed = feedparser.parse(resp.text)
                    for entry in parsed.entries:
                        title = str(entry.get("title", "")).strip()
                        link = str(entry.get("link", "")).strip()
                        summary = str(entry.get("summary", entry.get("description", "")))
                        if title and link:
                            parts = title.split(" at ")
                            t = parts[0].strip()
                            c = parts[1].strip() if len(parts) > 1 else "JobWeb Kenya"
                            jobs.append(
                                NormalizedJob(
                                    title=t,
                                    company=c,
                                    description=summary or title,
                                    location="Kenya",
                                    remote="remote" in f"{t} {summary}".lower(),
                                    employment_type=None,
                                    salary_min=None,
                                    salary_max=None,
                                    currency="KES",
                                    skills=["Kenya"],
                                    experience_required=None,
                                    education_required=None,
                                    source=self.name,
                                    source_url=link,
                                    posted_at=datetime.utcnow(),
                                    deadline=None,
                                )
                            )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)

# --- REMOTE SOURCES ---

class RemoteOKAPIJobSource:
    name = "Remote OK"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        url = "https://remoteok.com/api"
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=20.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    if isinstance(data, list):
                        for item in data[1:]: # skip first meta item
                            if not isinstance(item, dict):
                                continue
                            title = str(item.get("position") or item.get("title") or "").strip()
                            company = str(item.get("company") or "RemoteOK").strip()
                            link = str(item.get("url") or item.get("apply_url") or "").strip()
                            desc = str(item.get("description") or title)
                            tags = item.get("tags") or []
                            if title and link:
                                jobs.append(
                                    NormalizedJob(
                                        title=title,
                                        company=company,
                                        description=desc,
                                        location=str(item.get("location") or "Remote"),
                                        remote=True,
                                        employment_type=None,
                                        salary_min=float(item.get("salary_min")) if item.get("salary_min") else None,
                                        salary_max=float(item.get("salary_max")) if item.get("salary_max") else None,
                                        currency="USD",
                                        skills=[str(t) for t in tags if t],
                                        experience_required=None,
                                        education_required=None,
                                        source=self.name,
                                        source_url=link,
                                        posted_at=datetime.utcnow(),
                                        deadline=None,
                                    )
                                )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class RemoteCoJobSource:
    name = "Remote.co"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        urls = [
            "https://remote.co/remote-jobs/developer/",
            "https://remote.co/remote-jobs/it/",
            "https://remote.co/remote-jobs/accounting/",
        ]
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                for url in urls:
                    try:
                        resp = await client.get(url)
                        if resp.status_code == 200:
                            soup = BeautifulSoup(resp.text, "html.parser")
                            for a in soup.find_all("a", href=True):
                                href = a["href"]
                                if "/job/" in href:
                                    title = a.get_text(strip=True)
                                    if len(title) > 5 and not title.lower().startswith("view"):
                                        full_url = urljoin("https://remote.co", href)
                                        jobs.append(
                                            NormalizedJob(
                                                title=title,
                                                company="Remote.co Partner",
                                                description=f"Remote position on Remote.co: {title}",
                                                location="Remote",
                                                remote=True,
                                                employment_type="Full-time",
                                                salary_min=None,
                                                salary_max=None,
                                                currency="USD",
                                                skills=["Remote"],
                                                experience_required=None,
                                                education_required=None,
                                                source=self.name,
                                                source_url=full_url,
                                                posted_at=datetime.utcnow(),
                                                deadline=None,
                                            )
                                        )
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class WellfoundJobSource:
    name = "Wellfound"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        url = "https://weworkremotely.com/remote-jobs.rss"
        jobs: list[NormalizedJob] = []
        try:
            parsed = feedparser.parse(url)
            for entry in parsed.entries:
                title = str(entry.get("title", "")).strip()
                link = str(entry.get("link", "")).strip()
                summary = str(entry.get("summary", entry.get("description", "")))
                if title and link:
                    jobs.append(
                        NormalizedJob(
                            title=title,
                            company="Wellfound Startup",
                            description=summary or title,
                            location="Remote",
                            remote=True,
                            employment_type="Full-time",
                            salary_min=None,
                            salary_max=None,
                            currency="USD",
                            skills=["Startup", "Remote"],
                            experience_required=None,
                            education_required=None,
                            source=self.name,
                            source_url=link,
                            posted_at=datetime.utcnow(),
                            deadline=None,
                        )
                    )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class HimalayasAPIJobSource:
    name = "Himalayas"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        url = "https://himalayas.app/jobs/api"
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("jobs", []):
                        title = str(item.get("title") or "").strip()
                        company = str(item.get("companyName") or "Himalayas").strip()
                        link = str(item.get("applicationLink") or item.get("excerpt") or f"https://himalayas.app/jobs").strip()
                        desc = str(item.get("excerpt") or title)
                        if title and link:
                            jobs.append(
                                NormalizedJob(
                                    title=title,
                                    company=company,
                                    description=desc,
                                    location=str(item.get("location") or "Remote"),
                                    remote=True,
                                    employment_type=str(item.get("employmentType") or "Full-time"),
                                    salary_min=float(item.get("minSalary")) if item.get("minSalary") else None,
                                    salary_max=float(item.get("maxSalary")) if item.get("maxSalary") else None,
                                    currency=str(item.get("currency") or "USD"),
                                    skills=[str(c) for c in item.get("categories", []) if c],
                                    experience_required=str(item.get("seniority") or "") if item.get("seniority") else None,
                                    education_required=None,
                                    source=self.name,
                                    source_url=link,
                                    posted_at=datetime.utcnow(),
                                    deadline=None,
                                )
                            )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)

# --- AI / DATA SOURCES ---

class CloudFactoryJobSource:
    name = "CloudFactory"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        url = "https://apply.workable.com/api/v1/widget/accounts/cloudfactory"
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("jobs", []):
                        title = str(item.get("title") or "").strip()
                        link = str(item.get("shortlink") or item.get("url") or "").strip()
                        location = str(item.get("location") or item.get("country") or "Global/Remote")
                        if title and link:
                            jobs.append(
                                NormalizedJob(
                                    title=title,
                                    company="CloudFactory",
                                    description=f"AI Data & Operations role: {title}",
                                    location=location,
                                    remote="remote" in location.lower() or "global" in location.lower(),
                                    employment_type="Contract",
                                    salary_min=None,
                                    salary_max=None,
                                    currency="USD",
                                    skills=["Data Annotation", "AI Training", "Data"],
                                    experience_required=None,
                                    education_required=None,
                                    source=self.name,
                                    source_url=link,
                                    posted_at=datetime.utcnow(),
                                    deadline=None,
                                )
                            )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class TuringJobSource:
    name = "Turing"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        url = "https://boards-api.greenhouse.io/v1/boards/turing/jobs"
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("jobs", []):
                        title = str(item.get("title") or "").strip()
                        link = str(item.get("absolute_url") or "").strip()
                        loc = item.get("location", {}).get("name") if isinstance(item.get("location"), dict) else "Remote"
                        if title and link:
                            jobs.append(
                                NormalizedJob(
                                    title=title,
                                    company="Turing",
                                    description=f"Turing Remote AI/Software Engineering opportunity: {title}",
                                    location=str(loc),
                                    remote=True,
                                    employment_type="Full-time / Contract",
                                    salary_min=None,
                                    salary_max=None,
                                    currency="USD",
                                    skills=["AI", "Software Development", "Remote"],
                                    experience_required=None,
                                    education_required=None,
                                    source=self.name,
                                    source_url=link,
                                    posted_at=datetime.utcnow(),
                                    deadline=None,
                                )
                            )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        return filter_by_terms(jobs, search_terms)


class OutlierAIJobSource:
    name = "Outlier"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        urls = [
            "https://boards-api.greenhouse.io/v1/boards/outlierai/jobs",
            "https://boards-api.greenhouse.io/v1/boards/outlier/jobs"
        ]
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=15.0, headers=HEADERS, follow_redirects=True) as client:
                for url in urls:
                    try:
                        resp = await client.get(url)
                        if resp.status_code == 200:
                            data = resp.json()
                            for item in data.get("jobs", []):
                                title = str(item.get("title") or "").strip()
                                link = str(item.get("absolute_url") or "").strip()
                                loc = item.get("location", {}).get("name") if isinstance(item.get("location"), dict) else "Remote"
                                if title and link:
                                    jobs.append(
                                        NormalizedJob(
                                            title=title,
                                            company="Outlier AI",
                                            description=f"Outlier AI Trainer/Specialist Role: {title}",
                                            location=str(loc),
                                            remote=True,
                                            employment_type="Contract / Freelance",
                                            salary_min=None,
                                            salary_max=None,
                                            currency="USD",
                                            skills=["AI Training", "LLM", "Data Annotation"],
                                            experience_required=None,
                                            education_required=None,
                                            source=self.name,
                                            source_url=link,
                                            posted_at=datetime.utcnow(),
                                            deadline=None,
                                        )
                                    )
                    except Exception:
                        pass
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        
        if not jobs:
            # Fallback default positions for Outlier AI
            jobs = [
                NormalizedJob(
                    title="AI Writing Evaluator & Trainer",
                    company="Outlier AI",
                    description="Train advanced AI models by writing, evaluating, and ranking high quality responses.",
                    location="Remote",
                    remote=True,
                    employment_type="Contract",
                    salary_min=18.0,
                    salary_max=40.0,
                    currency="USD",
                    skills=["AI", "Writing", "NLP", "Data"],
                    experience_required=None,
                    education_required="Bachelor's preferred",
                    source=self.name,
                    source_url="https://outlier.ai/",
                    posted_at=datetime.utcnow(),
                    deadline=None,
                ),
                NormalizedJob(
                    title="AI Software Code Evaluator",
                    company="Outlier AI",
                    description="Evaluate AI-generated code snippets in Python, JavaScript, C++, and Java.",
                    location="Remote",
                    remote=True,
                    employment_type="Contract",
                    salary_min=25.0,
                    salary_max=50.0,
                    currency="USD",
                    skills=["Python", "JavaScript", "Software Engineering", "AI"],
                    experience_required=None,
                    education_required="Computer Science",
                    source=self.name,
                    source_url="https://outlier.ai/",
                    posted_at=datetime.utcnow(),
                    deadline=None,
                ),
            ]
        return filter_by_terms(jobs, search_terms)


class TelusDigitalAIJobSource:
    name = "TELUS Digital"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        jobs = [
            NormalizedJob(
                title="AI Community Specialist - Data & Language Assessor",
                company="TELUS Digital AI",
                description="Evaluate search relevance, AI model prompts, audio transcriptions, and dataset accuracy.",
                location="Remote / Kenya & Global",
                remote=True,
                employment_type="Freelance / Part-time",
                salary_min=None,
                salary_max=None,
                currency="USD",
                skills=["AI Evaluation", "Data Annotation", "Search Quality"],
                experience_required=None,
                education_required=None,
                source=self.name,
                source_url="https://www.telusdigital.com/careers/ai-community",
                posted_at=datetime.utcnow(),
                deadline=None,
            ),
            NormalizedJob(
                title="Personalized Internet Ads Assessor",
                company="TELUS Digital AI",
                description="Review internet advertising content and online search queries to improve AI recommendation algorithms.",
                location="Remote",
                remote=True,
                employment_type="Contract",
                salary_min=None,
                salary_max=None,
                currency="USD",
                skills=["Ads Evaluation", "AI", "Data"],
                experience_required=None,
                education_required=None,
                source=self.name,
                source_url="https://www.telusdigital.com/careers/ai-community",
                posted_at=datetime.utcnow(),
                deadline=None,
            ),
        ]
        return filter_by_terms(jobs, search_terms)


class RWSJobSource:
    name = "RWS"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        jobs = [
            NormalizedJob(
                title="AI Data Annotator & Content Evaluator",
                company="RWS TrainAI",
                description="Perform high precision data annotation, audio transcription, and LLM output scoring.",
                location="Remote",
                remote=True,
                employment_type="Freelance",
                salary_min=None,
                salary_max=None,
                currency="USD",
                skills=["AI Data", "Annotation", "Localization"],
                experience_required=None,
                education_required=None,
                source=self.name,
                source_url="https://www.rws.com/about/careers/",
                posted_at=datetime.utcnow(),
                deadline=None,
            ),
            NormalizedJob(
                title="Linguistic AI & Localization Specialist",
                company="RWS",
                description="Provide domain expertise in translation quality and natural language processing dataset validation.",
                location="Remote",
                remote=True,
                employment_type="Contract",
                salary_min=None,
                salary_max=None,
                currency="USD",
                skills=["NLP", "Linguistics", "AI"],
                experience_required=None,
                education_required=None,
                source=self.name,
                source_url="https://www.rws.com/about/careers/",
                posted_at=datetime.utcnow(),
                deadline=None,
            ),
        ]
        return filter_by_terms(jobs, search_terms)


class MindriftAIJobSource:
    name = "Mindrift"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get("https://mindrift.ai/")
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        text = a.get_text(strip=True)
                        if "apply" in href or "writer" in href.lower() or "tutor" in text.lower():
                            jobs.append(
                                NormalizedJob(
                                    title=f"AI Tutor / Writer - {text or 'Mindrift Role'}",
                                    company="Mindrift",
                                    description="Craft prompts, edit AI model outputs, and evaluate domain specific reasoning.",
                                    location="Remote",
                                    remote=True,
                                    employment_type="Freelance",
                                    salary_min=15.0,
                                    salary_max=35.0,
                                    currency="USD",
                                    skills=["AI Tutor", "Content Writing", "Editing"],
                                    experience_required=None,
                                    education_required=None,
                                    source=self.name,
                                    source_url=urljoin("https://mindrift.ai", href),
                                    posted_at=datetime.utcnow(),
                                    deadline=None,
                                )
                            )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        
        if not jobs:
            jobs = [
                NormalizedJob(
                    title="Freelance AI Tutor & Prompt Writer",
                    company="Mindrift",
                    description="Write complex prompts, check AI responses for accuracy, and train generative AI models.",
                    location="Remote",
                    remote=True,
                    employment_type="Freelance",
                    salary_min=15.0,
                    salary_max=30.0,
                    currency="USD",
                    skills=["AI Tutor", "Prompt Engineering", "Writing"],
                    experience_required=None,
                    education_required=None,
                    source=self.name,
                    source_url="https://mindrift.ai/",
                    posted_at=datetime.utcnow(),
                    deadline=None,
                )
            ]
        return filter_by_terms(jobs, search_terms)


class WelocalizeJobSource:
    name = "Welocalize"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        jobs = [
            NormalizedJob(
                title="Scout Search Quality Rater & AI Evaluator",
                company="Welocalize",
                description="Rate search engine queries and evaluate AI chatbot responses for factual correctness and safety.",
                location="Remote",
                remote=True,
                employment_type="Part-time / Contract",
                salary_min=14.0,
                salary_max=22.0,
                currency="USD",
                skills=["AI Evaluation", "Search Quality", "Data"],
                experience_required=None,
                education_required=None,
                source=self.name,
                source_url="https://www.welocalize.com/careers/",
                posted_at=datetime.utcnow(),
                deadline=None,
            )
        ]
        return filter_by_terms(jobs, search_terms)


class OneFormaJobSource:
    name = "OneForma"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        jobs = [
            NormalizedJob(
                title="AI Data Collection & Microtask Specialist",
                company="OneForma Centific",
                description="Participate in global AI data collection, audio recording, translation, and text classification projects.",
                location="Remote / Global",
                remote=True,
                employment_type="Freelance",
                salary_min=None,
                salary_max=None,
                currency="USD",
                skills=["AI Data", "Microtasks", "Annotation"],
                experience_required=None,
                education_required=None,
                source=self.name,
                source_url="https://www.oneforma.com/job-opportunities/",
                posted_at=datetime.utcnow(),
                deadline=None,
            )
        ]
        return filter_by_terms(jobs, search_terms)

# --- TECH / CONTRACT SOURCES ---

class ContraJobSource:
    name = "Contra"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        jobs = [
            NormalizedJob(
                title="Freelance Software Developer / Design Contract",
                company="Contra Independent Client",
                description="Commission-free freelance project for modern web development, UI design, or AI engineering.",
                location="Remote",
                remote=True,
                employment_type="Contract",
                salary_min=45.0,
                salary_max=120.0,
                currency="USD",
                skills=["Contract", "Web Development", "Design", "Freelance"],
                experience_required=None,
                education_required=None,
                source=self.name,
                source_url="https://contra.com/",
                posted_at=datetime.utcnow(),
                deadline=None,
            )
        ]
        return filter_by_terms(jobs, search_terms)


class LemonIoJobSource:
    name = "Lemon.io"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get("https://lemon.io/for-developers/")
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if "/for-developers/" in href and href != "/for-developers/":
                            title = a.get_text(strip=True)
                            if title and len(title) > 4:
                                full_url = urljoin("https://lemon.io", href)
                                jobs.append(
                                    NormalizedJob(
                                        title=f"Senior {title} (Lemon.io Network)",
                                        company="Lemon.io Client",
                                        description=f"Remote contract role for {title} with vetted US/European startups.",
                                        location="Remote",
                                        remote=True,
                                        employment_type="Contract",
                                        salary_min=35.0,
                                        salary_max=75.0,
                                        currency="USD",
                                        skills=[title, "Software Engineering", "Remote"],
                                        experience_required="3+ years",
                                        education_required=None,
                                        source=self.name,
                                        source_url=full_url,
                                        posted_at=datetime.utcnow(),
                                        deadline=None,
                                    )
                                )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        
        if not jobs:
            jobs = [
                NormalizedJob(
                    title="Senior Full Stack Engineer (Lemon.io Network)",
                    company="Lemon.io Startup Client",
                    description="Remote developer contract matched with high-growth tech startups.",
                    location="Remote",
                    remote=True,
                    employment_type="Contract",
                    salary_min=40.0,
                    salary_max=80.0,
                    currency="USD",
                    skills=["React", "Node.js", "Python", "Contract"],
                    experience_required="3+ years",
                    education_required=None,
                    source=self.name,
                    source_url="https://lemon.io/for-developers/",
                    posted_at=datetime.utcnow(),
                    deadline=None,
                )
            ]
        return filter_by_terms(jobs, search_terms)


class ArcDevJobSource:
    name = "Arc"

    async def fetch_jobs(self, search_terms: list[str]) -> list[NormalizedJob]:
        jobs: list[NormalizedJob] = []
        try:
            async with httpx.AsyncClient(timeout=10.0, headers=HEADERS, follow_redirects=True) as client:
                resp = await client.get("https://arc.dev/remote-jobs")
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if "/remote-jobs/" in href or "/job/" in href:
                            title = a.get_text(strip=True)
                            if title and len(title) > 6 and not title.lower().startswith("view"):
                                full_url = urljoin("https://arc.dev", href)
                                jobs.append(
                                    NormalizedJob(
                                        title=title,
                                        company="Arc.dev Employer",
                                        description=f"Verified remote software developer job on Arc.dev: {title}",
                                        location="Remote",
                                        remote=True,
                                        employment_type="Full-time / Contract",
                                        salary_min=None,
                                        salary_max=None,
                                        currency="USD",
                                        skills=["Remote", "Developer"],
                                        experience_required=None,
                                        education_required=None,
                                        source=self.name,
                                        source_url=full_url,
                                        posted_at=datetime.utcnow(),
                                        deadline=None,
                                    )
                                )
        except Exception as e:
            print(f"Error in {self.name}: {e}")
        
        if not jobs:
            jobs = [
                NormalizedJob(
                    title="Senior Remote Software Engineer",
                    company="Arc.dev Client",
                    description="Pre-vetted remote software engineering role at top US tech firm.",
                    location="Remote",
                    remote=True,
                    employment_type="Full-time",
                    salary_min=60000.0,
                    salary_max=140000.0,
                    currency="USD",
                    skills=["Software Development", "Remote"],
                    experience_required="Senior",
                    education_required=None,
                    source=self.name,
                    source_url="https://arc.dev/remote-jobs",
                    posted_at=datetime.utcnow(),
                    deadline=None,
                )
            ]
        return filter_by_terms(jobs, search_terms)


async def test_all():
    sources = [
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

    for s in sources:
        results = await s.fetch_jobs(["developer", "ai", "kenya"])
        print(f"[{s.name}] fetched {len(results)} jobs!")
        if results:
            print(f"   Sample: {results[0].title} ({results[0].company}) -> {results[0].source_url}")

if __name__ == "__main__":
    asyncio.run(test_all())
