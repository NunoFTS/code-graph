from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from backend.src.config.errors import ConfigError


def _parse_bool(value: str | None, *, default: bool = False) -> bool:
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"1", "true", "yes", "y", "on"}:
        return True
    if normalized in {"0", "false", "no", "n", "off"}:
        return False
    return default


@dataclass(frozen=True, slots=True)
class AppSettings:
    backend_dir: Path
    env_file: Path
    agents_toml: Path
    logs_dir: Path

    testing: bool
    gemini_api_key: str

    @classmethod
    def load(
        cls,
        *,
        backend_dir: Path | None = None,
        env_file: Path | None = None,
        agents_toml: Path | None = None,
    ) -> "AppSettings":
        resolved_backend_dir = backend_dir or Path(__file__).resolve().parents[2]
        resolved_env_file = env_file or (resolved_backend_dir / ".env")
        resolved_agents_toml = agents_toml or (resolved_backend_dir / "config" / "agents.toml")

        if resolved_env_file.exists():
            load_dotenv(dotenv_path=resolved_env_file, override=False, encoding="utf-8")

        testing = _parse_bool(os.getenv("TESTING"), default=False)

        # Prefer GEMINI_API_KEY, but allow GOOGLE_API_KEY for parity with the SDK.
        gemini_api_key = (os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or "").strip()
        if not gemini_api_key:
            raise ConfigError(
                "Missing GEMINI_API_KEY. Create backend/.env from backend/.env.example or set GEMINI_API_KEY in the environment."
            )

        if not resolved_agents_toml.exists():
            raise ConfigError(f"Missing agents config file: {resolved_agents_toml}")

        logs_dir = resolved_backend_dir / "_data" / "logs"

        return cls(
            backend_dir=resolved_backend_dir,
            env_file=resolved_env_file,
            agents_toml=resolved_agents_toml,
            logs_dir=logs_dir,
            testing=testing,
            gemini_api_key=gemini_api_key,
        )
