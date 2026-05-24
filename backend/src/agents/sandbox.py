from backend.src.sandbox.executor import run_code
from backend.src.graph.state import GraphState

def sandbox_executor(state: GraphState) -> dict:
    code = state.get("generated_code", "")

    result = run_code(code)

    return {
        **state,
        "execution_result": result
    }