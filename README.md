# AI Job Hunter

Full-stack job discovery and CV matching platform.

## Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI, SQLAlchemy (async), SQLite (dev) / PostgreSQL (prod)
- **AI:** Pluggable `AIService` (OpenAI-compatible API or heuristic fallback without `AI_API_KEY`)

## User flow

1. Register → upload CV (PDF/DOCX/TXT)
2. Review/edit profile and preferences
3. Run job search (Remotive API enabled by default)
4. View explainable match scores on the dashboard
5. Save jobs, track applications, generate cover letter drafts
6. Background scheduler re-searches every 6 hours (configurable)

## Architecture highlights

| Module | Location |
|--------|----------|
| AI abstraction | `backend/app/services/ai/service.py` |
| Job sources | `backend/app/job_sources/` |
| Matching weights | `.env` / `app/config.py` |
| Prompts | `backend/app/prompts/` |
| Admin API | `/api/admin/*` |

## Security & Protection

This repository is **production-secured**:
- 🔒 **Secrets Excluded:** `.env` and all private keys are strictly listed in `.gitignore`.
- 🛡️ **User Data Protected:** Uploaded CV files (`uploads/`) and SQLite databases (`*.db`) are ignored.
- ⚡ **API Key Safety:** Groq API keys are stored solely in environment variables and never logged or sent to client side.

This tool **does not** submit applications automatically or guarantee employment. Users open the original `source_url` and apply themselves.

