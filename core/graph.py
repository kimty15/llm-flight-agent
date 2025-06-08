from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from core.states import State
from core.nodes import Nodes

class TravelAssistantGraph:
    def __init__(self):
        self.nodes = Nodes()
        self.memory = MemorySaver()

    def create_graph(self):
        graph = StateGraph(State)

        graph.add_node("router", self.nodes.router)
        graph.add_node("food_search_agent", self.nodes.food_search_node)
        graph.add_node("retrieval_agent", self.nodes.retrieval_node)
        graph.add_node("ignore", self.nodes.ignore_node)

        # Set entry point
        graph.set_entry_point("router")

        # Add conditional edges
        graph.add_conditional_edges(
            "router",
            self.nodes.route_based_on_router,
            {
                "food_search_agent": "food_search_agent",
                "retrieval_agent": "retrieval_agent",
                "ignore": "ignore"
            }
        )
        # Add edges
        graph.add_edge("food_search_agent", END)
        graph.add_edge("retrieval_agent", END)
        graph.add_edge("ignore", END)

        assistant = graph.compile(checkpointer=self.memory)
        return assistant
    
async def chat_loop():
    """Main chat loop for interaction."""
    print("Welcome to Nha Trang Tourism Assistant!")
    print("You can ask about food places, attractions, transportation, and more in Nha Trang.")
    print("Type 'exit' to end the conversation.")
    print("-" * 50)
    
    # Initialize graph and state
    graph = TravelAssistantGraph()
    app = graph.create_graph()
    
    state = {
        "messages": [],
        "message_type": None
    }
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() == 'exit':
            print("\nGoodbye! Thank you for using Nha Trang Tourism Assistant.")
            break
        
        state["messages"].append({"role": "user", "content": user_input})
        
        try:
            result = await app.ainvoke(state, config={"configurable": {"thread_id": "1"}})
            assistant_message = result["messages"][-1].content
            print("\nAssistant:", assistant_message)
            state = result
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            print("Please try again with a different query.")

if __name__ == "__main__":
    import asyncio
    asyncio.run(chat_loop())        
        
        

