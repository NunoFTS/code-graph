from __future__ import annotations

import logging
from dataclasses import dataclass

from backend.src.agents.base import AgentContext, CodeGeneratorAgent, ValidatorAgent
from backend.src.api.gemini_client import GeminiClient
from backend.src.config.agents import load_agents_config
from backend.src.config.errors import ConfigError
from backend.src.config.settings import AppSettings
from backend.src.utils.prompts import load_prompt

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class AgentFactory:
    code_generator: CodeGeneratorAgent
    validator: ValidatorAgent

    @classmethod
    def from_settings(cls, settings: AppSettings) -> "AgentFactory":
        agents_cfg = load_agents_config(settings.agents_toml)

        gemini = GeminiClient(api_key=settings.gemini_api_key)

        generator_cfg = agents_cfg.require("code_generator")
        validator_cfg = agents_cfg.require("validator")

        _require_provider(generator_cfg.provider, agent="code_generator")
        _require_provider(validator_cfg.provider, agent="validator")

        _require_prompt_file(generator_cfg.prompt_file, agent="code_generator")
        _require_prompt_file(validator_cfg.prompt_file, agent="validator")

        logger.info(
            "agents_config_loaded",
            extra={
                "event": "agents_config_loaded",
                "agents_toml": str(settings.agents_toml),
                "generator_model": generator_cfg.model,
                "validator_model": validator_cfg.model,
            },
        )

        return cls(
            code_generator=CodeGeneratorAgent(
                context=AgentContext(name="code_generator", config=generator_cfg),
                llm=gemini,
            ),
            validator=ValidatorAgent(
                context=AgentContext(name="validator", config=validator_cfg),
                llm=gemini,
            ),
        )


def _require_provider(provider: str, *, agent: str) -> None:
    if provider.strip().lower() != "gemini":
        raise ConfigError(f"Unsupported provider '{provider}' for agent '{agent}'. Only 'gemini' is supported for now.")


def _require_prompt_file(prompt_file: str, *, agent: str) -> None:
    try:
        load_prompt(prompt_file)
    except FileNotFoundError as exc:
        raise ConfigError(f"Prompt file '{prompt_file}' for agent '{agent}' not found under backend/src/prompts/.") from exc
