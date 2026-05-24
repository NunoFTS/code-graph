from typing import TypedDict


class GraphState(TypedDict, total=False):
    input: str
    generated_code: str
    validation_result: str
    is_valid: bool
    attempts: int
    max_attempts: int

    execution_result: dict