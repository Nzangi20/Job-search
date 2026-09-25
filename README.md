# AI Job Hunter

Full-stack job discovery and CV matching platform.

## Stack

- **Frontend:** React, Vite, TypeScript, Tailwind CSS
- **Backend:** Python, FastAPI, SQLAlchemy (async), SQLite (dev) / PostgreSQL (prod)
- **AI:** Pluggable `AIService` (OpenAI-compatible API or heuristic fallback without `AI_API_KEY`)

## Quick start

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
# Optional: set AI_API_KEY in .env for real LLM analysis
uvicorn app.main:app --reload --port 8000
```

Default admin (seeded on first run):

- Email: `admin@aijobhunter.local`
- Password: `AdminPass123!`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

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

---

## Deployment Guide

### 1. Push to GitHub

```bash
# Initialize and commit (if not done)
git add .
git commit -m "Initial commit - Secured AI Job Hunter with Groq Integration"

# Link to your GitHub repository
git remote add origin https://github.com/YOUR_USERNAME/AI-Job-Hunter.git
git branch -M main
git push -u origin main
```

---

### 2. Backend Deployment (Render / Railway / Fly.io)

1. Create a new Web Service on **Render** or **Railway** connected to your GitHub repository.
2. Set the **Root Directory** to `backend`.
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Configure Environment Variables in your hosting dashboard:
   - `AI_PROVIDER`: `groq`
   - `AI_API_KEY`: `gsk_YOUR_GROQ_API_KEY`
   - `AI_BASE_URL`: `https://api.groq.com/openai/v1`
   - `AI_MODEL`: `openai/gpt-oss-120b`
   - `SECRET_KEY`: `<generate-a-long-random-string>`
   - `FRONTEND_URL`: `https://your-frontend-domain.vercel.app`

---

### 3. Frontend Deployment (Vercel / Netlify / Render Static Site)

1. Create a new Project on **Vercel** or **Netlify** connected to your GitHub repository.
2. Set the **Root Directory** to `frontend`.
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. Environment Variable:
   - `VITE_API_BASE_URL`: `https://your-backend-domain.onrender.com/api`

---

## Important

This tool **does not** submit applications automatically or guarantee employment. Users open the original `source_url` and apply themselves.

