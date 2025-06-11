"""Graph nodes for different conversation flows."""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from src.agents.retrieval.retrieval_agent import RetrievalAgent
from src.agents.food_agent.food_search_agent import FoodSearchAgent
from src.prompts.prompt_template import ROUTER_PROMPT
from src.core.states import State, Router
from src.core.config import settings
from src.utils.logger import get_logger

logger = get_logger(__name__)

class Nodes:
    """Graph nodes for handling different types of user queries."""
    
    def __init__(self):
        """Initialize agents."""
        self.retrieval_agent = RetrievalAgent()
        self.food_search_agent = FoodSearchAgent()
        logger.info("Nodes initialized with retrieval and food search agents")

    def router(self, state: State):
        """Route the query to the appropriate agent based on content."""
        message = state["messages"][-1]
        query = message.content
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", ROUTER_PROMPT),
            ("user", query)
        ])
        
        llm = ChatOpenAI(model=settings.LLM_MODEL, temperature=settings.TEMPERATURE)
        llm_router = llm.with_structured_output(Router)
        
        chain = prompt | llm_router
        result = chain.invoke({"query": query})
        
        logger.info(f"Router decision: {result.message_type} for query: {query}")
        return {"message_type": result.message_type}

    async def food_search_node(self, state: State) -> State:
        """Handle food-related queries."""
        message = state["messages"][-1]
        query = message.content
        logger.info(f"Processing food query: {query}")
        
        response = await self.food_search_agent.process_food_query(query)
        formatted_response = self.food_search_agent.format_response(response)
        
        return {
            "messages": [{"role": "assistant", "content": formatted_response}]
        }

    def retrieval_node(self, state: State) -> State:
        """Handle general information queries."""
        message = state["messages"][-1]
        query = message.content
        logger.info(f"Processing retrieval query: {query}")
        
        response = self.retrieval_agent.run(query)
        return {
            "messages": [{"role": "assistant", "content": response}]
        }

    def ignore_node(self, state: State) -> State:
        """Handle out-of-scope queries."""
        logger.info("Query marked as out-of-scope")
        return {
            "messages": [{"role": "assistant", "content": "I can only help with queries about Nha Trang. Please ask a question related to Nha Trang, Vietnam."}]
        }

    def route_based_on_router(self, state: State) -> str:
        """Determine which node to route to based on message type."""
        message_type = state.get("message_type")
        
        if message_type == "food_search_agent":
            return "food_search_agent"
        elif message_type == "retrieval_agent":
            return "retrieval_agent"
        elif message_type == "ignore":
            return "ignore"
        else:
            logger.warning(f"Unknown message type: {message_type}, defaulting to ignore")
            return "ignore" 