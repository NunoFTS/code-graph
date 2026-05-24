from backend.src.graph.state import GraphState

import logging

logger = logging.getLogger(__name__)

def route_after_validation(state: GraphState) -> str:
    if state.get("error"):
        logger.info("route_end_error", extra={"event": "route_end_error", "error": str(state.get("error"))[:500]})
        return "end"

    attempts = state.get("attempts", 0)
    max_attempts = state.get("max_attempts", 3)
    is_valid = bool(state.get("is_valid"))

    if attempts >= max_attempts:
        logger.info(
            "route_end_max_attempts",
            extra={"event": "route_end_max_attempts", "attempts": attempts, "max_attempts": max_attempts},
        )
        return "end"

    if is_valid:
        logger.info("route_end_valid", extra={"event": "route_end_valid", "attempts": attempts})
        return "end"

    logger.info(
        "route_retry_generator",
        extra={"event": "route_retry_generator", "attempts": attempts, "max_attempts": max_attempts},
    )
    return "code_generator"
