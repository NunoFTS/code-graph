from __future__ import annotations

import json
import logging

from backend.src.config.errors import ConfigError

logger = logging.getLogger(__name__)


class GeminiClient:
    def __init__(self, *, api_key: str) -> None:
        try:
            from google import genai  # type: ignore[import-not-found]
        except ModuleNotFoundError as exc:
            raise ConfigError(
                "Missing dependency 'google-genai'. Install backend requirements: pip install -r backend/requirements.txt"
            ) from exc

        self._client = genai.Client(api_key=api_key)

    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        output_json: bool,
    ) -> str:
        from google.genai import types  # type: ignore[import-not-found]

        response_mime_type = "application/json" if output_json else "text/plain"

        response = self._client.models.generate_content(
            model=model,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=temperature,
                response_mime_type=response_mime_type,
            ),
        )

        try:
            text = (response.text or "").strip()
        except Exception as exc:
            logger.exception(
                "gemini_response_text_error",
                extra={
                    "event": "gemini_response_text_error",
                    "model": model,
                    "response_mime_type": response_mime_type,
                },
            )
            raise RuntimeError("Gemini response did not contain a usable text payload.") from exc

        if not text:
            logger.error(
                "gemini_empty_response",
                extra={
                    "event": "gemini_empty_response",
                    "model": model,
                    "response_mime_type": response_mime_type,
                },
            )
            raise RuntimeError("Gemini returned an empty response.")

        if output_json:
            try:
                json.loads(text)
            except Exception:
                logger.warning(
                    "gemini_invalid_json",
                    extra={
                        "event": "gemini_invalid_json",
                        "model": model,
                        "response_mime_type": response_mime_type,
                        "text_preview": text[:500],
                    },
                )

        return text
