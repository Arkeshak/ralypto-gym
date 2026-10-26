from app.ai.clients.base import LLMClient
from app.ai.clients.gemini_client import GeminiClient
from app.ai.clients.mock_client import MockLLM
from app.core.config import settings


def get_llm_client() -> LLMClient:
    if settings.GEMINI_API_KEY:
        return GeminiClient(api_key=settings.GEMINI_API_KEY, model=settings.LLM_MODEL)
    return MockLLM()
