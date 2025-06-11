"""LangGraph workflow for the travel assistant."""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from src.core.states import State
from src.core.nodes import Nodes
from src.utils.logger import get_logger

logger = get_logger(__name__)

class TravelAssistantGraph:
    """Main graph orchestrator for the travel assistant."""
    
    def __init__(self):
        """Initialize the graph with nodes and memory."""
        self.nodes = Nodes()
        self.memory = MemorySaver()
        logger.info("TravelAssistantGraph initialized")

    def create_graph(self):
        """Create and configure the conversation graph."""
        graph = StateGraph(State)

        # Add nodes
        graph.add_node("router", self.nodes.router)
        graph.add_node("food_search_agent", self.nodes.food_search_node)
        graph.add_node("retrieval_agent", self.nodes.retrieval_node)
        graph.add_node("ignore", self.nodes.ignore_node)

        # Set entry point
        graph.set_entry_point("router")

        # Add conditional edges based on router decision
        graph.add_conditional_edges(
            "router",
            self.nodes.route_based_on_router,
            {
                "food_search_agent": "food_search_agent",
                "retrieval_agent": "retrieval_agent",
                "ignore": "ignore"
            }
        )
        
        # Add terminal edges
        graph.add_edge("food_search_agent", END)
        graph.add_edge("retrieval_agent", END)
        graph.add_edge("ignore", END)

        # Compile with memory checkpointer
        assistant = graph.compile(checkpointer=self.memory)
        logger.info("Graph compiled successfully")
        
        return assistant 