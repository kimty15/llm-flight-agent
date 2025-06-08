import os
from serpapi import GoogleSearch
from pydantic_ai import Agent, RunContext
import asyncio
from param.params import FoodPlace, FoodSearchResponse, FoodQuery

from prompts.prompt_template import FOOD_SEARCH_PROMPT

from dotenv import load_dotenv
load_dotenv()

class FoodSearchAgent:
    def __init__(self):
        self.agent = Agent(
            "openai:gpt-4o",
            output_type=FoodQuery,
            food_search_prompt=FOOD_SEARCH_PROMPT
        )

    def search_food_places(self, query: str, location: str = None) -> FoodQuery:
        """
        Search for food places using SerpAPI.
        
        Args:
            query: The search query (e.g., "pizza", "sushi", "italian food")
            location: Optional location to search in (e.g., "New York", "London")
        
        Returns:
            FoodSearchResponse containing a list of food places with their details
        """
        # Default to Nha Trang if no location specified
        if not location:
            location = "Nha Trang, Việt Nam"
        elif "vietnam" not in location.lower() and "việt nam" not in location.lower():
            location = f"{location}, Việt Nam"
        # print(query)
        # print(location)
        params = {
                "engine": "google_maps",
                "q": f"{query} {location}",  # Combine query with location
                "type": "search",
                "location": location,
                "hl": "vi",
                "gl": "vn",
                "google_domain": "google.com.vn",
                "api_key": os.getenv("SERPAPI_API_KEY")
            }
            
        search = GoogleSearch(params)
        results = search.get_dict()
            
        places = []
        if "local_results" in results:
                # Take only the first 2 results
            for place in results["local_results"][:2]:
                food_place = FoodPlace(
                        name=place.get("title", ""),
                        address=place.get("address", ""),
                        rating=place.get("rating"),
                        price_level=place.get("price"),
                        type=place.get("type")
                    )
                places.append(food_place)
        
        return FoodSearchResponse(
                places=places,
                location=location
            )



    async def process_food_query(self, user_query: str):
        """
        Process a natural language food search query using the agent.
        
        Args:
            user_query: The user's natural language query about food places
        
        Returns:
            FoodSearchResponse containing search results
        """
        # Use the agent to parse the query
        agent_result = await self.agent.run(user_query)
        parsed_query = agent_result.output  # Access the output field which contains our FoodQuery
        # print(f"Parsed query: {parsed_query}")

        if not parsed_query.is_nha_trang and parsed_query.location:
            return None
        else:
            # Perform the actual search
            return self.search_food_places(
                query=parsed_query.query,
                location=parsed_query.location
            )
    
    def format_response(self, response: FoodSearchResponse) -> str:
        """Format the search results into a readable string."""
        if not response or not response.places:
            return "I couldn't find any food places matching your query in Nha Trang."
        
        formatted = f"Here are some food places in {response.location}:\n\n"
        for place in response.places:
            formatted += f"- {place.name}\n"
            formatted += f"  Address: {place.address}\n"
            if place.rating:
                formatted += f"  Rating: {place.rating}\n"
            if place.price_level:
                formatted += f"  Price Level: {place.price_level}\n"
            if place.type:
                formatted += f"  Type: {place.type}\n"
            formatted += "\n"
        
        return formatted    # Example usage:
async def main():
    # Initialize the agent
    agent = FoodSearchAgent()
    
    # Test queries
    test_queries = [
        "Tôi muốn tìm quán Phở ở Nha Trang",
        "Nhà hàng hải sản ngon ở Nha Trang",
        "Quán cafe đẹp ở Nha Trang",
        "Tìm quán ăn Việt Nam ở Nha Trang",
        "Nhà hàng Nhật Bản ở Nha Trang"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        response = await agent.process_food_query(query)
        formatted_response = agent.format_response(response)
        print(formatted_response)
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(main())