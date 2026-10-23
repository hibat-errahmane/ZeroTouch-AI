import httpx
from app.config import Settings

async def status(settings: Settings) -> dict:
    try:
        async with httpx.AsyncClient(timeout=3.0, trust_env=False) as client:
            response = await client.get(f"{settings.ollama_url}/api/tags")
            response.raise_for_status()
            models = response.json()["models"]
            names = [item["name"] for item in models]
            if not all(isinstance(name, str) for name in names):
                raise ValueError("Invalid model names")
        return {"available": True, "model": settings.ollama_model,
                "model_installed": settings.ollama_model in names, "models": names}
    except (httpx.HTTPError, ValueError, KeyError, TypeError):
        return {"available": False, "model": settings.ollama_model,
                "model_installed": False, "models": [],
                "message": "Ollama is unavailable or returned an invalid response. Document preview still works."}
