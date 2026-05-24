from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from backend.src.config.agents import AgentModelConfig
from backend.src.graph.state import GraphState
from backend.src.utils.prompts import load_prompt
from backend.src.utils.template import safe_format


class LLMClient(Protocol):
    def generate(
        self,
        prompt: str,
        *,
        model: str,
        temperature: float,
        output_json: bool,
    ) -> str: ...


@dataclass(frozen=True, slots=True)
class AgentContext:
    name: str
    config: AgentModelConfig


class BaseAgent:
    def __init__(self, *, context: AgentContext, llm: LLMClient) -> None:
        self._context = context
        self._llm = llm
        self._logger = logging.getLogger(f"agents.{context.name}")

    def __call__(self, state: GraphState) -> GraphState:
        if state.get("error"):
            self._logger.info(
                "agent_skipped_due_to_error",
                extra={"event": "agent_skipped_due_to_error", "agent": self._context.name},
            )
            return {}

        cfg = self._context.config

        try:
            prompt_template = load_prompt(cfg.prompt_file)
            prompt = safe_format(prompt_template, state)
        except Exception:
            self._logger.exception(
                "agent_prompt_error",
                extra={"event": "agent_prompt_error", "agent": self._context.name, "prompt_file": cfg.prompt_file},
            )
            return self._on_error(state, error="prompt_render_failed")

        self._logger.debug(
            "agent_prompt_ready",
            extra={
                "event": "agent_prompt_ready",
                "agent": self._context.name,
                "model": cfg.model,
                "temperature": cfg.temperature,
                "output_json": cfg.output_json,
                "prompt_file": cfg.prompt_file,
                "prompt_chars": len(prompt),
            },
        )

        try:
            output = self._llm.generate(
                prompt,
                model=cfg.model,
                temperature=cfg.temperature,
                output_json=cfg.output_json,
            )
        except Exception as exc:
            self._logger.exception(
                "agent_llm_error",
                extra={
                    "event": "agent_llm_error",
                    "agent": self._context.name,
                    "model": cfg.model,
                    "temperature": cfg.temperature,
                    "output_json": cfg.output_json,
                },
            )
            return self._on_error(state, error=str(exc)[:500])

        self._logger.debug(
            "agent_llm_done",
            extra={"event": "agent_llm_done", "agent": self._context.name, "output_chars": len(output)},
        )

        return self.handle_output(state, output)

    def handle_output(self, state: GraphState, output: str) -> GraphState:
        raise NotImplementedError

    def _on_error(self, state: GraphState, *, error: str) -> GraphState:
        return {"error": f"{self._context.name}: {error}"}


class CodeGeneratorAgent(BaseAgent):
    def handle_output(self, state: GraphState, output: str) -> GraphState:
        attempts = state.get("attempts", 0) + 1
        return {"generated_code": output, "attempts": attempts}

    def _on_error(self, state: GraphState, *, error: str) -> GraphState:
        attempts = state.get("attempts", 0) + 1
        return {"error": f"{self._context.name}: {error}", "attempts": attempts}


class ValidatorAgent(BaseAgent):
    def __call__(self, state: GraphState) -> GraphState:
        if state.get("error"):
            error = str(state.get("error"))
            self._logger.info(
                "validator_skipped_due_to_error",
                extra={"event": "validator_skipped_due_to_error", "error": error[:500]},
            )
            return {"validation_result": f"FAIL: {error}", "is_valid": False}

        return super().__call__(state)

    def handle_output(self, state: GraphState, output: str) -> GraphState:
        is_valid = output.strip().upper().startswith("PASS")
        return {"validation_result": output, "is_valid": is_valid}
