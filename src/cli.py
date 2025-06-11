"""Command-line interface for the Nha Trang Tourism Assistant."""

import asyncio
from src.core.graph import TravelAssistantGraph
from src.utils.logger import get_logger

logger = get_logger(__name__)

async def chat_loop():
    """Main chat loop for CLI interaction."""
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
            result = await app.ainvoke(state, config={"configurable": {"thread_id": "cli_session"}})
            assistant_message = result["messages"][-1].content
            print("\nAssistant:", assistant_message)
            state = result
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}", exc_info=True)
            print(f"\nError: {str(e)}")
            print("Please try again with a different query.")

def main():
    """Main CLI entry point."""
    asyncio.run(chat_loop())

if __name__ == "__main__":
    main() 