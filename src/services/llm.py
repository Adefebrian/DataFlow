"""
LLM Service — Multi-Model Async Client
========================================
Supports three model tiers:
  FAST     → Qwen/Qwen3-8B              (JSON, classification, validation)
  BALANCED → Qwen/Qwen3-Next-80B-A3B-Instruct (analytics, features, narratives)
  REASONING→ deepseek-ai/DeepSeek-R1-0528     (insights, patterns, deep analysis)

All models served via Hyperbolic API (OpenAI-compatible endpoint).
"""

import asyncio
import json
import logging
import re
from typing import Optional

import aiohttp

from src.config import get_settings
from src.models.types import (
    LLMTier,
    get_model_for_task,
    get_temperature_for_task,
    get_max_tokens_for_task,
)

logger = logging.getLogger(__name__)

HYPERBOLIC_BASE_URL = "https://api.hyperbolic.xyz/v1"


class HyperbolicLLMClient:
    """
    Async HTTP client for Hyperbolic API — OpenAI-compatible.
    Handles all three model tiers with per-task configuration.
    """

    def __init__(self):
        settings = get_settings()
        self.api_key = settings.HYPERBOLIC_API_KEY
        self.base_url = HYPERBOLIC_BASE_URL
        self.available = bool(self.api_key)

        if not self.available:
            logger.warning("HYPERBOLIC_API_KEY not set — LLM features disabled.")

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    async def complete(
        self,
        prompt: str,
        model: str = LLMTier.BALANCED,
        temperature: float = 0.1,
        max_tokens: int = 2048,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        """
        Core completion method. Returns the text content of the first choice.
        """
        if not self.available:
            return ""

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        payload: dict = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        # DeepSeek-R1 doesn't support response_format JSON mode
        if json_mode and "deepseek" not in model.lower():
            payload["response_format"] = {"type": "json_object"}

        timeout = aiohttp.ClientTimeout(total=120)

        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers=self._headers(),
                    json=payload,
                ) as resp:
                    if resp.status != 200:
                        text = await resp.text()
                        logger.error(f"Hyperbolic API error {resp.status}: {text[:300]}")
                        return ""

                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]

                    # DeepSeek-R1 wraps reasoning in <think>...</think> — strip it
                    if "deepseek" in model.lower():
                        content = self._strip_thinking(content)

                    return content.strip()

        except asyncio.TimeoutError:
            logger.error(f"Hyperbolic API timeout for model {model}")
            return ""
        except Exception as e:
            logger.error(f"Hyperbolic API error: {e}")
            return ""

    def _strip_thinking(self, content: str) -> str:
        """Strip DeepSeek-R1 <think>...</think> reasoning traces from output."""
        # Remove <think> blocks
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        # Strip leading/trailing whitespace
        return content.strip()

    async def complete_for_task(
        self,
        prompt: str,
        task_name: str,
        system: str | None = None,
        json_mode: bool = False,
    ) -> str:
        """
        Convenience method: auto-selects model, temperature, max_tokens by task name.
        """
        model = get_model_for_task(task_name)
        temperature = get_temperature_for_task(task_name)
        max_tokens = get_max_tokens_for_task(task_name)

        logger.info(f"[LLM] task={task_name} model={model} temp={temperature} max_tok={max_tokens}")

        return await self.complete(
            prompt=prompt,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system=system,
            json_mode=json_mode,
        )

    async def complete_json(
        self,
        prompt: str,
        task_name: str,
        system: str | None = None,
        fallback: dict | None = None,
    ) -> dict:
        """
        Complete and parse JSON response. Returns fallback dict on failure.
        """
        raw = await self.complete_for_task(
            prompt=prompt,
            task_name=task_name,
            system=system,
            json_mode=True,
        )

        if not raw:
            return fallback or {}

        try:
            # Strip markdown code fences if present
            clean = re.sub(r"```(?:json)?\s*", "", raw).replace("```", "").strip()
            return json.loads(clean)
        except json.JSONDecodeError:
            # Try to extract JSON from within the response
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except Exception:
                    pass
            logger.warning(f"Failed to parse JSON from LLM response: {raw[:200]}")
            return fallback or {}

    # ── Legacy compatibility ──────────────────────────────────────────────────

    async def generate_insights(self, prompt: str) -> Optional[str]:
        """Legacy method for backward compat."""
        return await self.complete(
            prompt=prompt,
            model=LLMTier.REASONING,
            temperature=0.6,
            max_tokens=4000,
        )


# ── Singleton ────────────────────────────────────────────────────────────────

_client: HyperbolicLLMClient | None = None


async def get_llm() -> HyperbolicLLMClient:
    global _client
    if _client is None:
        _client = HyperbolicLLMClient()
    return _client


def get_llm_service() -> HyperbolicLLMClient:
    """Sync accessor for legacy compatibility."""
    global _client
    if _client is None:
        _client = HyperbolicLLMClient()
    return _client


# backward compat alias
llm_service = get_llm_service()
