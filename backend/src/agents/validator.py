from backend.src.api.gemini_client import generate
from backend.src.utils.prompts import load_prompt


def validator(state: dict) -> dict:
    prompt = load_prompt("validator.txt")

    code = state.get("generated_code", "")

    full_prompt = f"{prompt}\n{code}"

    result = generate(full_prompt)

    is_valid = "PASS" in result.upper()

    return {
        **state,
        "validation_result": result,
        "is_valid": is_valid
    }