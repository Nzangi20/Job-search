import asyncio
import os
import httpx
from app.config import get_settings

async def test_groq():
    url = "https://api.groq.com/openai/v1/chat/completions"
    key = os.getenv("AI_API_KEY") or get_settings().ai_api_key
    if not key:
        print("No AI_API_KEY set.")
        return
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }
    models = ['openai/gpt-oss-120b', 'openai/gpt-oss-20b', 'qwen/qwen3.8-27b']
    async with httpx.AsyncClient(timeout=15.0) as client:
        for m in models:
            payload = {
                "model": m,
                "messages": [
                    {"role": "user", "content": "Hello! Reply with JSON: {\"status\": \"ok\"}"}
                ],
                "temperature": 0.2
            }
            resp = await client.post(url, headers=headers, json=payload)
            print(f"Model {m} -> Status: {resp.status_code}")
            if resp.status_code == 200:
                data = resp.json()
                print("   OUTPUT:", data['choices'][0]['message']['content'])
                break
            else:
                print("   ERROR:", resp.text[:200])

if __name__ == "__main__":
    asyncio.run(test_groq())
