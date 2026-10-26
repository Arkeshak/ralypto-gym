from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class LLMClient(ABC):
    @abstractmethod
    def generate(
        self,
        prompt: str,
        system: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Generate text or JSON response from LLM."""
        pass
