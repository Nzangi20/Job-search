import json
import re
from abc import ABC, abstractmethod

import httpx

from app.config import get_settings
from app.prompts import (
    APPLICATION_ANSWERS,
    COVER_LETTER,
    CV_ANALYSIS,
    JOB_ANALYSIS,
    JOB_QUESTION_ANSWER,
    MATCH_COMPARISON,
)


def _extract_json(text: str) -> dict | list:
    text = text.strip()
    # Remove markdown code fences
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?\s*```\s*$", "", text)
        text = text.strip()
    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    # Try to find JSON object or array in the text
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        if start == -1:
            continue
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            c = text[i]
            if escape:
                escape = False
                continue
            if c == "\\":
                escape = True
                continue
            if c == '"':
                in_string = not in_string
                continue
            if in_string:
                continue
            if c == start_char:
                depth += 1
            elif c == end_char:
                depth -= 1
                if depth == 0:
                    candidate = text[start : i + 1]
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        break
    # Last resort: original text
    return json.loads(text)


class AIService(ABC):
    @abstractmethod
    async def analyze_cv(self, cv_text: str) -> dict:
        pass

    @abstractmethod
    async def analyze_job(self, job_description: str) -> dict:
        pass

    @abstractmethod
    async def calculate_match(self, candidate: dict, job_analysis: dict) -> dict:
        pass

    @abstractmethod
    async def generate_cover_letter(self, cv_text: str, job_description: str) -> str:
        pass

    @abstractmethod
    async def answer_application_question(
        self, cv_text: str, job_description: str, questions: list[str]
    ) -> list[dict]:
        pass

    @abstractmethod
    async def ask_job_question(
        self, cv_text: str, job_description: str, question: str
    ) -> str:
        pass


class OpenAICompatibleAIService(AIService):
    def __init__(self) -> None:
        self.settings = get_settings()
        self.fallback = HeuristicAIService()

    async def _chat(self, system: str, user: str) -> str:
        if not self.settings.ai_api_key:
            raise RuntimeError("AI_API_KEY is not configured")

        url = f"{self.settings.ai_base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.settings.ai_api_key}",
            "Content-Type": "application/json",
        }

        # Build model priorities
        candidate_models = [self.settings.ai_model]
        if "groq" in self.settings.ai_provider.lower() or "groq.com" in self.settings.ai_base_url.lower():
            groq_models = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b"]
            for m in groq_models:
                if m not in candidate_models:
                    candidate_models.append(m)

        last_error = None
        for model in candidate_models:
            payload = {
                "model": model,
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
            }
            for attempt in range(3):
                try:
                    async with httpx.AsyncClient(timeout=120.0) as client:
                        resp = await client.post(url, headers=headers, json=payload)
                        if resp.status_code == 429:
                            import asyncio
                            await asyncio.sleep(2 ** attempt)
                            last_error = f"Rate limited by AI provider ({model})"
                            continue
                        if resp.status_code == 401:
                            raise RuntimeError("AI API key is invalid or expired. Check AI_API_KEY in .env")
                        if resp.status_code >= 400:
                            body = resp.text[:500]
                            if resp.status_code == 404 or "model" in body.lower():
                                last_error = f"Model {model} unavailable ({resp.status_code}): {body}"
                                break
                            raise RuntimeError(f"AI API error ({resp.status_code}): {body}")
                        data = resp.json()
                        return data["choices"][0]["message"]["content"]
                except httpx.TimeoutException:
                    last_error = f"AI API request timed out for model {model}"
                    continue
                except RuntimeError:
                    raise
                except Exception as exc:
                    last_error = str(exc)
                    continue
        raise RuntimeError(f"AI API failed: {last_error}")

    async def analyze_cv(self, cv_text: str) -> dict:
        try:
            content = await self._chat(CV_ANALYSIS, cv_text[:50000])
            return _extract_json(content)
        except Exception as exc:
            print(f"[AIService] analyze_cv API error, using fallback: {exc}")
            return await self.fallback.analyze_cv(cv_text)

    async def analyze_job(self, job_description: str) -> dict:
        try:
            content = await self._chat(JOB_ANALYSIS, job_description[:50000])
            return _extract_json(content)
        except Exception as exc:
            print(f"[AIService] analyze_job API error, using fallback: {exc}")
            return await self.fallback.analyze_job(job_description)

    async def calculate_match(self, candidate: dict, job_analysis: dict) -> dict:
        try:
            user = json.dumps({"candidate": candidate, "job": job_analysis})
            content = await self._chat(MATCH_COMPARISON, user)
            return _extract_json(content)
        except Exception as exc:
            print(f"[AIService] calculate_match API error, using fallback: {exc}")
            return await self.fallback.calculate_match(candidate, job_analysis)

    async def generate_cover_letter(self, cv_text: str, job_description: str) -> str:
        try:
            user = f"CV:\n{cv_text[:30000]}\n\nJob:\n{job_description[:20000]}"
            return await self._chat(COVER_LETTER, user)
        except Exception as exc:
            print(f"[AIService] generate_cover_letter API error, using fallback: {exc}")
            return await self.fallback.generate_cover_letter(cv_text, job_description)

    async def answer_application_question(
        self, cv_text: str, job_description: str, questions: list[str]
    ) -> list[dict]:
        try:
            user = json.dumps(
                {
                    "cv_excerpt": cv_text[:30000],
                    "job_excerpt": job_description[:20000],
                    "questions": questions,
                }
            )
            content = await self._chat(APPLICATION_ANSWERS, user)
            result = _extract_json(content)
            return result if isinstance(result, list) else result.get("answers", [])
        except Exception as exc:
            print(f"[AIService] answer_application_question API error, using fallback: {exc}")
            return await self.fallback.answer_application_question(cv_text, job_description, questions)

    async def ask_job_question(
        self, cv_text: str, job_description: str, question: str
    ) -> str:
        try:
            user = f"Candidate CV:\n{cv_text[:30000]}\n\nJob Description:\n{job_description[:20000]}\n\nCandidate Question:\n{question}"
            return await self._chat(JOB_QUESTION_ANSWER, user)
        except Exception as exc:
            print(f"[AIService] ask_job_question API error, using fallback: {exc}")
            return await self.fallback.ask_job_question(cv_text, job_description, question)


class HeuristicAIService(AIService):
    """Fallback when no API key — broad heuristic parsing for local dev across all job categories."""

    async def analyze_cv(self, cv_text: str) -> dict:
        lines = [ln.strip() for ln in cv_text.splitlines() if ln.strip()]
        text_lower = cv_text.lower()

        # Multi-category skill dictionary
        skill_catalog = [
            "Python", "SQL", "JavaScript", "React", "FastAPI", "Machine Learning", "Data Analysis",
            "Marketing", "SEO", "Content Writing", "Copywriting", "Social Media", "Sales", "CRM",
            "Salesforce", "Customer Service", "Customer Support", "Project Management", "Agile",
            "Financial Analysis", "Accounting", "Excel", "Bookkeeping", "Human Resources", "Recruiting",
            "Graphic Design", "Figma", "Photoshop", "UI/UX", "Operations", "Logistics", "Legal", "Nursing"
        ]
        
        found_skills = [s for s in skill_catalog if s.lower() in text_lower]

        # Infer titles based on detected domain keywords
        titles = []
        if any(k in text_lower for k in ["marketing", "seo", "social media"]):
            titles.extend(["Marketing Specialist", "Content Marketer", "Digital Marketing Manager"])
        if any(k in text_lower for k in ["sales", "account executive", "crm"]):
            titles.extend(["Sales Representative", "Account Executive", "Business Development Manager"])
        if any(k in text_lower for k in ["finance", "accounting", "excel", "bookkeeping"]):
            titles.extend(["Financial Analyst", "Accountant", "Bookkeeper"])
        if any(k in text_lower for k in ["hr", "human resources", "recruiting"]):
            titles.extend(["HR Generalist", "Recruiter", "People Operations Manager"])
        if any(k in text_lower for k in ["support", "customer service", "helpdesk"]):
            titles.extend(["Customer Support Specialist", "Client Services Representative"])
        if any(k in text_lower for k in ["design", "figma", "ui/ux", "photoshop"]):
            titles.extend(["Graphic Designer", "UI/UX Designer", "Creative Specialist"])
        if any(k in text_lower for k in ["python", "software", "developer", "sql", "react"]):
            titles.extend(["Software Developer", "Python Developer", "Data Analyst", "Full-Stack Engineer"])
        
        if not titles:
            titles = ["Operations Coordinator", "Project Assistant", "Specialist"]

        seniority = "Junior"
        if any(k in text_lower for k in ["senior", "lead", "head of", "director", "manager"]):
            seniority = "Senior" if "senior" in text_lower or "lead" in text_lower else "Mid Level"

        return {
            "professional_summary": lines[0][:500] if lines else "",
            "skills": found_skills,
            "programming_languages": [s for s in found_skills if s in {"Python", "JavaScript", "SQL", "R", "C++", "Java"}],
            "frameworks": [s for s in found_skills if s in {"React", "FastAPI", "Django", "Vue", "Angular"}],
            "tools": [s for s in found_skills if s in {"Excel", "Salesforce", "Figma", "Jira", "Photoshop", "Hubspot", "QuickBooks"}],
            "databases": ["SQL"] if "sql" in text_lower else [],
            "education": [],
            "certifications": [],
            "experience": [],
            "projects": [],
            "potential_job_titles": list(dict.fromkeys(titles)),
            "seniority_level": seniority,
            "personal_info": {},
        }

    async def analyze_job(self, job_description: str) -> dict:
        text = job_description.lower()
        skill_catalog = [
            "python", "sql", "javascript", "react", "fastapi", "docker", "excel",
            "marketing", "seo", "sales", "salesforce", "crm", "customer service",
            "accounting", "finance", "recruiting", "figma", "design", "copywriting"
        ]
        required = [s.title() for s in skill_catalog if s in text]
        return {
            "required_skills": required[:6],
            "preferred_skills": [],
            "experience_requirement": "0-2 years" if any(k in text for k in ["junior", "entry"]) else "",
            "education_requirement": "",
            "seniority": "Junior" if "junior" in text or "entry" in text else ("Senior" if "senior" in text else "Mid Level"),
            "location": "Remote" if "remote" in text else "",
            "remote_status": "remote" in text,
            "employment_type": "full-time",
            "salary": {},
            "responsibilities": [],
            "application_deadline": None,
        }

    async def calculate_match(self, candidate: dict, job_analysis: dict) -> dict:
        c_skills = {s.lower() for s in candidate.get("skills", [])}
        required = job_analysis.get("required_skills") or []
        missing = [s for s in required if s.lower() not in c_skills]
        matching = [s for s in required if s.lower() in c_skills]
        return {
            "matching_skills": matching,
            "missing_required_skills": missing,
            "matching_experience": [],
            "experience_gaps": [],
            "role_compatibility": "medium",
            "location_compatibility": "high",
            "education_compatibility": "high",
            "match_highlights": [f"You have {s} experience" for s in matching[:5]],
            "gap_highlights": [f"{s} is listed as required but not in your CV" for s in missing[:5]],
        }

    async def generate_cover_letter(self, cv_text: str, job_description: str) -> str:
        return (
            "Dear Hiring Manager,\n\n"
            "I am writing to express my interest in this role. "
            "Please review my attached CV and customize this draft before submitting.\n\n"
            "Sincerely,\n[Your Name]"
        )

    async def answer_application_question(
        self, cv_text: str, job_description: str, questions: list[str]
    ) -> list[dict]:
        return [
            {
                "question": q,
                "suggested_answer": "Draft answer — review and edit using your CV before submitting.",
            }
            for q in questions
        ]

    async def ask_job_question(
        self, cv_text: str, job_description: str, question: str
    ) -> str:
        return f"Based on your CV and this job posting: To address '{question}', review the key requirements and highlight your relevant project experience."



def get_ai_service() -> AIService:
    settings = get_settings()
    if settings.ai_api_key:
        return OpenAICompatibleAIService()
    return HeuristicAIService()
