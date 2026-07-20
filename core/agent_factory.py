"""Build the controlled LangGraph trip planner workflow."""

from __future__ import annotations

from typing import TYPE_CHECKING

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

from config.settings import Settings, get_settings
from core.nodes import (
    analyze_request,
    generate_response,
    retrieve_knowledge,
    search_food_if_needed,
)
from core.state import TripState

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def build_trip_planner_graph(
    *,
    settings: Settings | None = None,
) -> CompiledStateGraph:
    s = settings or get_settings()

    graph = StateGraph(TripState)
    graph.add_node("analyze_request", analyze_request)
    graph.add_node("retrieve_knowledge", retrieve_knowledge)
    graph.add_node("search_food_if_needed", search_food_if_needed)
    graph.add_node("generate_response", lambda state: generate_response(state, s))

    graph.add_edge(START, "analyze_request")
    graph.add_edge("analyze_request", "retrieve_knowledge")
    graph.add_edge("retrieve_knowledge", "search_food_if_needed")
    graph.add_edge("search_food_if_needed", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile(checkpointer=MemorySaver())
