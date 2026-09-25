import asyncio
from app.config import get_settings
from app.services.ai.service import get_ai_service

async def main():
    settings = get_settings()
    settings.cache_clear() if hasattr(settings, "cache_clear") else None
    print("AI Provider:", settings.ai_provider)
    print("AI Model:", settings.ai_model)
    print("AI Base URL:", settings.ai_base_url)
    print("AI Key Configured:", bool(settings.ai_api_key))

    ai = get_ai_service()
    print("Service class:", type(ai).__name__)

    sample_cv = """
    Jane Doe - Senior Full Stack Engineer
    Skills: Python, FastAPI, React, TypeScript, PostgreSQL, Docker, AI
    Experience: 5 years building scalable web applications and REST APIs.
    """
    print("\nTesting AI CV analysis via Groq...")
    res = await ai.analyze_cv(sample_cv)
    print("Analysis output:")
    print(res)

if __name__ == "__main__":
    asyncio.run(main())
