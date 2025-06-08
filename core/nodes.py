from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from agents.retrieval.retrieval_agent import RetrievalAgent
from agents.food_agent.food_search_agent import FoodSearchAgent
from prompts.prompt_template import ROUTER_PROMPT
from core.states import State, Router
from config.setting import LLM_MODEL, TEMPERATURE

class Nodes:
    def __init__(self):
        self.retrieval_agent = RetrievalAgent()
        self.food_search_agent = FoodSearchAgent()

    def router(self, state: State):
        """Route the query to the appropriate agent based on content."""
        message = state["messages"][-1]
        query = message.content
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", ROUTER_PROMPT),
            ("user", query)
        ])
        
        llm = ChatOpenAI(model=LLM_MODEL, temperature=TEMPERATURE)
        llm_router = llm.with_structured_output(Router)
        
        chain = prompt | llm_router
        result = chain.invoke({"query": query})
        
        return {"message_type": result.message_type}

    async def food_search_node(self, state: State) -> State:
        """Handle food-related queries."""
        message = state["messages"][-1]
        query = message.content
        response = await self.food_search_agent.process_food_query(query)
        formatted_response = self.food_search_agent.format_response(response)
        
        return {
            "messages": [{"role": "assistant", "content": formatted_response}]
        }

    def retrieval_node(self, state: State) -> State:
        """Handle general information queries."""
        message = state["messages"][-1]
        query = message.content
        response = self.retrieval_agent.run(query)
        return {
            "messages": [{"role": "assistant", "content": response}]
        }

    def ignore_node(self, state: State) -> State:
        """Handle out-of-scope queries."""
        return {
            "messages": [{"role": "assistant", "content": "I can only help with queries about Nha Trang. Please ask a question related to Nha Trang, Vietnam."}]
        }

    def route_based_on_router(self, state: State) -> str:
        """Determine which node to route to based on message type."""
        if state["message_type"] == "food_search_agent":
            return "food_search_agent"
        elif state["message_type"] == "retrieval_agent":
            return "retrieval_agent"
        elif state["message_type"] == "ignore":
            return "ignore"