from backend.src.graph.state import GraphState

def route_after_validation(state: GraphState) -> str:
    if state.get("attempts", 0) >= state.get("max_attempts", 3):
        return "end"

    if state.get("is_valid"):
        return "end"

    return "code_generator"