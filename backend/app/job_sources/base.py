from dataclasses import dataclass
from datetime import datetime
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse


@dataclass
class NormalizedJob:
    title: str
    company: str
    description: str
    location: str | None
    remote: bool
    employment_type: str | None
    salary_min: float | None
    salary_max: float | None
    currency: str | None
    skills: list[str]
    experience_required: str | None
    education_required: str | None
    source: str
    source_url: str
    posted_at: datetime | None
    deadline: datetime | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "title": self.title,
            "company": self.company,
            "description": self.description,
            "location": self.location,
            "remote": self.remote,
            "employment_type": self.employment_type,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "currency": self.currency,
            "skills": self.skills,
            "experience_required": self.experience_required,
            "education_required": self.education_required,
            "source": self.source,
            "source_url": self.source_url,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "deadline": self.deadline.isoformat() if self.deadline else None,
        }


def normalize_url(url: str) -> str:
    parsed = urlparse(url.strip().lower())
    query = parse_qs(parsed.query, keep_blank_values=True)
    for key in list(query.keys()):
        if key.startswith("utm_") or key in {"ref", "source", "gh_src"}:
            del query[key]
    clean_query = urlencode({k: v[0] for k, v in query.items()}, doseq=False)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", clean_query, ""))
