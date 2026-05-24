def route_after_validation(state: dict) -> str:
    if state.get("is_valid"):
        return "end"
    return "generator"