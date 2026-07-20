from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from serpapi import GoogleSearch

from config.settings import Settings, get_settings
from param.params import FoodPlace, FoodQuery, FoodSearchResponse
from prompts.prompt_template import FOOD_SEARCH_PROMPT


class FoodSearchAgent:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self._chain: Any | None = None

    def _build_chain(self) -> Any:
        if self._chain is None:
            llm = ChatOpenAI(
                model=self.settings.llm_model,
                temperature=self.settings.temperature,
            )
            parser = llm.with_structured_output(FoodQuery)
            self._chain = (
                ChatPromptTemplate.from_messages(
                    [
                        ("system", FOOD_SEARCH_PROMPT),
                        ("user", "{query}"),
                    ]
                )
                | parser
            )
        return self._chain

    def search_food_places(
        self, query: str, location: str | None = None
    ) -> FoodSearchResponse:
        if not location:
            location = self.settings.default_location
        elif "vietnam" not in location.lower() and "việt nam" not in location.lower():
            location = f"{location}, Việt Nam"

        params = {
            "engine": "google_maps",
            "q": f"{query} {location}",
            "type": "search",
            "location": location,
            "hl": self.settings.search_language,
            "gl": self.settings.search_country,
            "google_domain": self.settings.google_domain,
            "api_key": self.settings.serpapi_api_key,
        }

        search = GoogleSearch(params)
        results = search.get_dict()

        places: list[FoodPlace] = []
        if "local_results" in results:
            for place in results["local_results"][: self.settings.food_max_results]:
                places.append(
                    FoodPlace(
                        name=place.get("title", ""),
                        address=place.get("address", ""),
                        rating=place.get("rating"),
                        price_level=place.get("price"),
                        type=place.get("type"),
                    )
                )

        return FoodSearchResponse(places=places, location=location)

    def parse_food_query(self, user_query: str) -> FoodQuery:
        return self._build_chain().invoke({"query": user_query})

    def format_response(self, response: FoodSearchResponse | None) -> str:
        if not response or not response.places:
            return "I could not find matching meal stops in Nha Trang right now."

        lines = [f"Meal stop options in {response.location}:"]
        for place in response.places:
            bits = [place.name]
            if place.type:
                bits.append(place.type)
            if place.rating:
                bits.append(f"rating {place.rating}")
            if place.price_level:
                bits.append(f"price {place.price_level}")
            lines.append(f"- {' | '.join(bits)}")
            if place.address:
                lines.append(f"  Address: {place.address}")
        return "\n".join(lines)
