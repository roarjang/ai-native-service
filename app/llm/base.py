from collections.abc import AsyncIterator
from typing import Protocol


class LLMClient(Protocol):
    async def generate(self, prompt: str) -> str:
        """프롬프트를 받아 텍스트 응답을 반환."""
        ...

    def stream(self, prompt: str) -> AsyncIterator[str]:
        """프롬프트를 받아 텍스트 응답을 순서대로 반환."""
        ...
