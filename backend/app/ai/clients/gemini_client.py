import json
from typing import Any, Dict, Optional
import httpx
from app.ai.clients.base import LLMClient
from app.ai.clients.mock_client import MockLLM
from app.core.config import settings


class GeminiClient(LLMClient):
    """Google Gemini LLM client with automatic fallback to MockLLM."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.LLM_MODEL or "gemini-1.5-flash"
        self.fallback = MockLLM()

    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not self.api_key:
            return self.fallback.generate(prompt, system, json_schema)

        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
            contents = []
            if system:
                contents.append({"role": "user", "parts": [{"text": f"SYSTEM: {system}"}]})
            contents.append({"role": "user", "parts": [{"text": prompt}]})

            payload: Dict[str, Any] = {"contents": contents}
            if json_schema:
                payload["generationConfig"] = {
                    "responseMimeType": "application/json"
                }

            with httpx.Client(timeout=15.0) as client:
                res = client.post(url, json=payload)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            return self.fallback.generate(prompt, system, json_schema)
        except Exception:
            return self.fallback.generate(prompt, system, json_schema)
