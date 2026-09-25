from datetime import datetime

from pydantic import BaseModel, Field


class ResumeOut(BaseModel):
    id: int
    filename: str
    content_type: str
    is_active: bool
    created_at: datetime
    has_analysis: bool = False
    analysis: dict | None = None
    extracted_text: str | None = None

    model_config = {"from_attributes": True}


class JobOut(BaseModel):
    id: int
    title: str
    company: str
    description: str
    location: str | None
    remote: bool
    employment_type: str | None
    salary_min: float | None
    salary_max: float | None
    currency: str | None
    experience_required: str | None
    education_required: str | None
    source: str
    source_url: str
    posted_at: datetime | None
    deadline: datetime | None
    skills: list[str] = Field(default_factory=list)
    analysis: dict | None = None

    model_config = {"from_attributes": True}


class JobMatchOut(BaseModel):
    id: int
    overall_score: float
    component_scores: dict | None
    match_reasons: list | None
    gap_reasons: list | None
    status: str
    job: JobOut
    resume_id: int | None = None
    resume_filename: str | None = None

    model_config = {"from_attributes": True}


class JobSearchRequest(BaseModel):
    query: str | None = None
    min_match: float | None = None
    employment_type: str | None = None
    location: str | None = None
    experience: str | None = None
    salary_min: float | None = None
    salary_max: float | None = None
    skills: list[str] = Field(default_factory=list)


class ApplicationCreate(BaseModel):
    job_id: int
    status: str = "applied"
    notes: str | None = None


class ApplicationUpdate(BaseModel):
    status: str | None = None
    notes: str | None = None


class ApplicationOut(BaseModel):
    id: int
    job_id: int
    status: str
    notes: str | None
    job: JobOut | None = None

    model_config = {"from_attributes": True}


class SearchOut(BaseModel):
    id: int
    query: str
    jobs_found: int
    created_at: datetime

    model_config = {"from_attributes": True}


class NotificationSettingsUpdate(BaseModel):
    email_enabled: bool | None = None
    telegram_enabled: bool | None = None
    telegram_chat_id: str | None = None


class CoverLetterRequest(BaseModel):
    job_id: int


class ApplicationQuestionRequest(BaseModel):
    job_id: int
    questions: list[str]


class JobQuestionRequest(BaseModel):
    job_id: int
    question: str

