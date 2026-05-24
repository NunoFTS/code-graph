from langgraph.graph import StateGraph, END

from backend.src.graph.state import GraphState
from backend.src.agents.generator import code_generator
from backend.src.agents.validator import validator
from backend.src.agents.orchestrator import route_after_validation


def build_graph():
    builder = StateGraph(GraphState)

    # Nodes
    builder.add_node("generator", code_generator)
    builder.add_node("validator", validator)

    # Flow
    builder.set_entry_point("generator")

    builder.add_edge("generator", "validator")

    builder.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "generator": "generator",
            "end": END
        }
    )

    return builder.compile()
