"""Food search agent for restaurant and food place queries."""

import os
import asyncio
from serpapi import GoogleSearch
from pydantic_ai import Agent, RunContext
from dotenv import load_dotenv

from src.param.params import FoodPlace, FoodSearchResponse, FoodQuery
from src.prompts.prompt_template import FOOD_SEARCH_PROMPT
from src.core.config import settings
from src.utils.logger import get_logger

load_dotenv()
logger = get_logger(__name__)

class FoodSearchAgent:
    """Agent for handling food and restaurant search queries."""
    
    def __init__(self):
        """Initialize the food search agent."""
        self.agent = Agent(
            "openai:gpt-4o",
            output_type=FoodQuery,
            food_search_prompt=FOOD_SEARCH_PROMPT
        )
        logger.info("FoodSearchAgent initialized")

    def search_food_places(self, query: str, location: str = None) -> FoodSearchResponse:
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
            location = settings.DEFAULT_LOCATION
        elif "vietnam" not in location.lower() and "việt nam" not in location.lower():
            location = f"{location}, Việt Nam"
        
        logger.info(f"Searching for food places: {query} in {location}")
        
        try:
            params = {
                "engine": settings.SEARCH_ENGINE,
                "q": f"{query} {location}",
                "type": "search",
                "location": location,
                "hl": settings.LANGUAGE,
                "gl": settings.COUNTRY,
                "google_domain": settings.GOOGLE_DOMAIN,
                "api_key": os.getenv("SERPAPI_API_KEY")
            }
            
            search = GoogleSearch(params)
            results = search.get_dict()
            
            places = []
            if "local_results" in results:
                # Take only the first MAX_RESULTS results
                for place in results["local_results"][:settings.MAX_RESULTS]:
                    food_place = FoodPlace(
                        name=place.get("title", ""),
                        address=place.get("address", ""),
                        rating=place.get("rating"),
                        price_level=place.get("price"),
                        type=place.get("type")
                    )
                    places.append(food_place)
            
            logger.info(f"Found {len(places)} food places")
            return FoodSearchResponse(places=places, location=location)
            
        except Exception as e:
            logger.error(f"Error searching food places: {str(e)}")
            return FoodSearchResponse(places=[], location=location)

    async def process_food_query(self, user_query: str):
        """
        Process a natural language food search query using the agent.
        
        Args:
            user_query: The user's natural language query about food places
        
        Returns:
            FoodSearchResponse containing search results
        """
        try:
            logger.info(f"Processing food query: {user_query}")
            
            # Use the agent to parse the query
            agent_result = await self.agent.run(user_query)
            parsed_query = agent_result.output
            
            logger.info(f"Parsed query: {parsed_query}")

            if not parsed_query.is_nha_trang and parsed_query.location:
                logger.info("Query is not related to Nha Trang")
                return None
            else:
                # Perform the actual search
                return self.search_food_places(
                    query=parsed_query.query,
                    location=parsed_query.location
                )
        except Exception as e:
            logger.error(f"Error processing food query: {str(e)}")
            return None
    
    def format_response(self, response: FoodSearchResponse) -> str:
        """Format the search results into a readable string."""
        if not response or not response.places:
            return "I couldn't find any food places matching your query in Nha Trang."
        
        formatted = f"Here are some food places in {response.location}:\n\n"
        for place in response.places:
            formatted += f"🍽️ **{place.name}**\n"
            formatted += f"📍 Address: {place.address}\n"
            if place.rating:
                formatted += f"⭐ Rating: {place.rating}\n"
            if place.price_level:
                formatted += f"💰 Price Level: {place.price_level}\n"
            if place.type:
                formatted += f"🏷️ Type: {place.type}\n"
            formatted += "\n"
        
        return formatted 