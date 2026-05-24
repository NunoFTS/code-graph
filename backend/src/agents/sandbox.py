import logging

from backend.src.sandbox.executor import run_code
from backend.src.graph.state import GraphState

logger = logging.getLogger(__name__)

def sandbox_executor(state: GraphState) -> dict:
    if state.get("error"):
        logger.info("sandbox_skipped_due_to_error", extra={"event": "sandbox_skipped_due_to_error"})
        return {}

    code = state.get("generated_code", "")

    if not str(code).strip():
        return {
            "execution_result": {
                "stdout": "",
                "stderr": "",
                "returncode": None,
                "timeout": False,
                "timeout_s": 0.0,
                "error": "No generated code to execute",
            }
        }

    result = run_code(code)

    logger.debug(
        "sandbox_executed",
        extra={
            "event": "sandbox_executed",
            "returncode": result.get("returncode"),
            "timeout": result.get("timeout"),
            "stdout_chars": len(result.get("stdout") or ""),
            "stderr_chars": len(result.get("stderr") or ""),
        },
    )

    return {
        "execution_result": result
    }
