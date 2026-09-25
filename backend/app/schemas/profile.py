from pydantic import BaseModel, Field


class ProfileUpdate(BaseModel):
    professional_level: str | None = None
    professional_summary: str | None = None
    preferred_roles: list[str] = Field(default_factory=list)
    preferred_locations: list[str] = Field(default_factory=list)
    employment_types: list[str] = Field(default_factory=list)
    minimum_salary: float | None = None
    salary_currency: str | None = None
    experience_level: str | None = None
    work_authorization: str | None = None
    keywords: list[str] = Field(default_factory=list)
    search_terms: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    structured_data: dict | None = None


class ProfileOut(BaseModel):
    id: int
    professional_level: str | None
    professional_summary: str | None
    preferred_roles: list | None
    preferred_locations: list | None
    employment_types: list | None
    minimum_salary: float | None
    salary_currency: str | None
    experience_level: str | None
    work_authorization: str | None
    keywords: list | None
    search_terms: list | None
    skills: list[str] = Field(default_factory=list)
    structured_data: dict | None

    model_config = {"from_attributes": True}


class AISettingsOut(BaseModel):
    ai_provider: str
    ai_base_url: str
    ai_model: str
    ai_api_key_configured: bool
    ai_api_key_masked: str | None


class AISettingsUpdate(BaseModel):
    ai_provider: str | None = None
    ai_base_url: str | None = None
    ai_model: str | None = None
    ai_api_key: str | None = None

