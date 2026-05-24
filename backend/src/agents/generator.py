from backend.src.api.gemini_client import generate
from backend.src.utils.prompts import load_prompt


def code_generator(state: dict) -> dict:
    user_input = state.get("input", "")

    prompt = load_prompt("generator.txt")

    full_prompt = f"{prompt}\n{user_input}"

    code = generate(full_prompt)

    return {
        **state,
        "generated_code": code
    }
