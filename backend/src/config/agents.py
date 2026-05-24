from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from backend.src.config.errors import ConfigError

try:
    import tomllib  # type: ignore[attr-defined]
except ModuleNotFoundError:  # pragma: no cover (Python <3.11)
    import tomli as tomllib  # type: ignore[no-redef]


@dataclass(frozen=True, slots=True)
class AgentModelConfig:
    provider: str
    model: str
    temperature: float
    prompt_file: str
    output_json: bool


@dataclass(frozen=True, slots=True)
class AgentsConfig:
    agents: dict[str, AgentModelConfig]

    def require(self, name: str) -> AgentModelConfig:
        try:
            return self.agents[name]
        except KeyError as exc:
            raise ConfigError(f"Missing agent config for '{name}' in agents.toml.") from exc


def load_agents_config(path: Path) -> AgentsConfig:
    if not path.exists():
        raise ConfigError(f"Missing agents config file: {path}")

    try:
        with path.open("rb") as f:
            data = tomllib.load(f)
    except Exception as exc:  # TOMLDecodeError lives in tomllib but differs across implementations
        raise ConfigError(f"Failed to parse agents config TOML: {path}") from exc

    agents_raw = data.get("agents")
    if not isinstance(agents_raw, dict):
        raise ConfigError(f"Invalid agents.toml: expected a top-level [agents] table in {path}")

    agents: dict[str, AgentModelConfig] = {}
    for agent_name, cfg in agents_raw.items():
        if not isinstance(agent_name, str) or not isinstance(cfg, dict):
            raise ConfigError(f"Invalid agent entry under [agents] in {path}: {agent_name!r}")

        provider = _require_str(cfg, "provider", path=path, agent=agent_name)
        model = _require_str(cfg, "model", path=path, agent=agent_name)
        temperature = _require_float(cfg, "temperature", path=path, agent=agent_name)
        prompt_file = _require_str(cfg, "prompt_file", path=path, agent=agent_name)
        output_json = _require_bool(cfg, "output_json", path=path, agent=agent_name)

        agents[agent_name] = AgentModelConfig(
            provider=provider,
            model=model,
            temperature=temperature,
            prompt_file=prompt_file,
            output_json=output_json,
        )

    return AgentsConfig(agents=agents)


def _require_str(cfg: dict[str, Any], key: str, *, path: Path, agent: str) -> str:
    value = cfg.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ConfigError(f"Invalid agents.toml: [{agent}] '{key}' must be a non-empty string in {path}")
    return value.strip()


def _require_float(cfg: dict[str, Any], key: str, *, path: Path, agent: str) -> float:
    value = cfg.get(key)
    if not isinstance(value, (int, float)):
        raise ConfigError(f"Invalid agents.toml: [{agent}] '{key}' must be a number in {path}")
    return float(value)


def _require_bool(cfg: dict[str, Any], key: str, *, path: Path, agent: str) -> bool:
    value = cfg.get(key)
    if not isinstance(value, bool):
        raise ConfigError(f"Invalid agents.toml: [{agent}] '{key}' must be a boolean in {path}")
    return value
