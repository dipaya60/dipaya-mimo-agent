"""
MiMo API Client (OpenAI-compatible)
Async-first with retry logic, token counting, and JSON mode.
"""

import asyncio
import json
import time
import logging
from typing import Any, Dict, List, Optional, AsyncIterator
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class CompletionResponse:
    content: str
    model: str
    usage: Dict[str, int]
    finish_reason: str
    latency_ms: float


class MiMoClientError(Exception):
    pass


class MiMoClient:
    """
    Async client for MiMo-V2.5-Pro via OpenAI-compatible API.
    
    Features:
    - Async/await support with httpx
    - Exponential backoff retry
    - Token counting
    - JSON mode for structured output
    - Streaming support
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.openai.com/v1",
        model: str = "mimo-v2.5-pro",
        max_tokens: int = 4096,
        temperature: float = 0.7,
        max_retries: int = 3,
        timeout: int = 60,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.max_retries = max_retries
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
        self._total_tokens_used = 0

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()

    def _count_tokens(self, text: str) -> int:
        """Approximate token count (~4 chars per token for English)."""
        return len(text) // 4

    def _estimate_messages_tokens(self, messages: List[ChatMessage]) -> int:
        total = 0
        for msg in messages:
            total += 4 + self._count_tokens(msg.content)
        return total

    async def chat(
        self,
        messages: List[ChatMessage],
        json_mode: bool = False,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> CompletionResponse:
        """Send a chat completion request with retry logic."""
        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "max_tokens": max_tokens or self.max_tokens,
            "temperature": temperature if temperature is not None else self.temperature,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        last_error = None
        for attempt in range(self.max_retries):
            try:
                client = await self._get_client()
                start = time.monotonic()
                resp = await client.post("/chat/completions", json=payload)
                latency_ms = (time.monotonic() - start) * 1000

                if resp.status_code == 429:
                    wait = 2 ** attempt
                    logger.warning(f"Rate limited, retrying in {wait}s (attempt {attempt+1})")
                    await asyncio.sleep(wait)
                    continue

                resp.raise_for_status()
                data = resp.json()

                content = data["choices"][0]["message"]["content"]
                usage = data.get("usage", {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0})
                self._total_tokens_used += usage.get("total_tokens", 0)

                return CompletionResponse(
                    content=content,
                    model=data.get("model", self.model),
                    usage=usage,
                    finish_reason=data["choices"][0].get("finish_reason", "stop"),
                    latency_ms=latency_ms,
                )
            except httpx.HTTPStatusError as e:
                last_error = e
                wait = 2 ** attempt
                logger.warning(f"HTTP {e.response.status_code}, retrying in {wait}s")
                await asyncio.sleep(wait)
            except httpx.RequestError as e:
                last_error = e
                wait = 2 ** attempt
                logger.warning(f"Request error: {e}, retrying in {wait}s")
                await asyncio.sleep(wait)

        raise MiMoClientError(f"Failed after {self.max_retries} retries: {last_error}")

    async def chat_text(self, prompt: str, system: Optional[str] = None) -> str:
        """Convenience: single prompt -> string response."""
        messages = []
        if system:
            messages.append(ChatMessage(role="system", content=system))
        messages.append(ChatMessage(role="user", content=prompt))
        resp = await self.chat(messages)
        return resp.content

    async def chat_json(self, prompt: str, system: Optional[str] = None) -> Dict[str, Any]:
        """Convenience: prompt -> parsed JSON response."""
        messages = []
        if system:
            messages.append(ChatMessage(role="system", content=system))
        messages.append(ChatMessage(role="user", content=prompt))
        resp = await self.chat(messages, json_mode=True)
        try:
            return json.loads(resp.content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            import re
            match = re.search(r"```(?:json)?\s*\n(.*?)\n```", resp.content, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise

    @property
    def total_tokens_used(self) -> int:
        return self._total_tokens_used


class MiMoClientSync:
    """Synchronous wrapper for MiMoClient."""

    def __init__(self, **kwargs):
        self._async_client = MiMoClient(**kwargs)
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def _get_loop(self):
        if self._loop is None or self._loop.is_closed():
            self._loop = asyncio.new_event_loop()
        return self._loop

    def chat(self, messages: List[ChatMessage], **kwargs) -> CompletionResponse:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_client.chat(messages, **kwargs))

    def chat_text(self, prompt: str, system: Optional[str] = None) -> str:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_client.chat_text(prompt, system))

    def chat_json(self, prompt: str, system: Optional[str] = None) -> Dict[str, Any]:
        loop = self._get_loop()
        return loop.run_until_complete(self._async_client.chat_json(prompt, system))

    def close(self):
        if self._loop and not self._loop.is_closed():
            self._loop.run_until_complete(self._async_client.close())
            self._loop.close()
