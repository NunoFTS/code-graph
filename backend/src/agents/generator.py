from backend.src.api.gemini_client import generate
from backend.src.utils.prompts import load_prompt
from backend.src.graph.state import GraphState


def code_generator(state: GraphState) -> GraphState:
    user_input = state.get("input", "")

    prompt = load_prompt("generator.txt")
    full_prompt = f"{prompt}\n{user_input}"
    code = generate(full_prompt)

    attempts = state.get("attempts", 0) + 1

    return {
        **state,
        "generated_code": code,
        "attempts": attempts
    }
