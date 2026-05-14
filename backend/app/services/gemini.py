"""
LLM service backed by OpenRouter (OpenAI-compatible API).

Uses httpx to call OpenRouter's /chat/completions endpoint.
Keeps the class named GeminiService so no other files need changing.

Note: NVIDIA Nemotron 3 Nano Omni is text-only — image bytes are ignored
and the filename/hint is used for plant identification text matching.
"""
from __future__ import annotations

import json
import re
from typing import Any

import httpx

from app.core.config import Settings

OPENROUTER_BASE = "https://openrouter.ai/api/v1"


class GeminiService:  # named GeminiService to avoid renaming all imports
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self._api_key = settings.openrouter_api_key
        self._model = settings.openrouter_model
        self._timeout = settings.openrouter_timeout

    @property
    def enabled(self) -> bool:
        return bool(self._api_key)

    # ------------------------------------------------------------------
    # Public helpers
    # ------------------------------------------------------------------

    def generate_json(
        self,
        prompt: str,
        schema_hint: str,
        image_bytes: bytes | None = None,
        mime_type: str | None = None,
    ) -> dict[str, Any]:
        """
        Send a prompt to OpenRouter and parse the JSON response.
        image_bytes are intentionally ignored — Nemotron Nano is text-only.
        """
        full_prompt = (
            f"{prompt}\n\n"
            f"Respond with valid JSON only — no markdown, no extra text.\n"
            f"Schema:\n{schema_hint}"
        )
        raw = self._chat(full_prompt)
        return self._parse_json(raw)

    def generate_text(self, prompt: str) -> str:
        return self._chat(prompt).strip()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _chat(self, prompt: str) -> str:
        if not self._api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is not set. Please add it to your .env file."
            )

        url = f"{OPENROUTER_BASE}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "http://localhost:5173",  # OpenRouter requires this
            "X-Title": "PlantIQ",
        }
        payload = {
            "model": self._model,
            "messages": [{"role": "user", "content": prompt}],
        }

        print(f"DEBUG: Calling OpenRouter model={self._model}")
        try:
            resp = httpx.post(url, json=payload, headers=headers, timeout=self._timeout)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]
        except httpx.ConnectError:
            raise RuntimeError("Cannot connect to OpenRouter. Check your internet connection.")
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                f"OpenRouter HTTP error {exc.response.status_code}: {exc.response.text}"
            )

    def _parse_json(self, text: str) -> dict[str, Any]:
        cleaned = text.strip()
        # Strip markdown fences if present
        if cleaned.startswith("```"):
            match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL)
            if match:
                cleaned = match.group(1).strip()
        # Extract first JSON object if model adds surrounding text
        if not cleaned.startswith("{"):
            match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
            if match:
                cleaned = match.group(0)
        return json.loads(cleaned)
