from langgraph.graph import StateGraph, END

from backend.src.graph.state import GraphState
from backend.src.agents.factory import AgentFactory
from backend.src.agents.orchestrator import route_after_validation
from backend.src.agents.sandbox import sandbox_executor


def build_graph(factory: AgentFactory):
    builder = StateGraph(GraphState)

    builder.add_node("code_generator", factory.code_generator)
    builder.add_node("sandbox", sandbox_executor)
    builder.add_node("validator", factory.validator)

    builder.set_entry_point("code_generator")

    builder.add_edge("code_generator", "sandbox")
    builder.add_edge("sandbox", "validator")

    builder.add_conditional_edges(
        "validator",
        route_after_validation,
        {
            "code_generator": "code_generator",
            "end": END
        }
    )

    return builder.compile()
