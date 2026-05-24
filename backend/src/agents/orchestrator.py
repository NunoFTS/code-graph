from backend.src.graph.state import GraphState


def route_after_validation(state: GraphState) -> str:
    is_valid = state.get("is_valid", False)
    attempts = state.get("attempts", 0)
    max_attempts = state.get("max_attempts", 3)

    # Route to end if validation passed
    if is_valid:
        return "end"

    # Route to end if max attempts reached (prevent infinite loops)
    if attempts >= max_attempts:
        return "end"

    # Otherwise retry generation
    return "generator"