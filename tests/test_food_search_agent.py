from agents.food_agent.food_search_agent import FoodSearchAgent
from param.params import FoodPlace, FoodSearchResponse


def test_format_response_empty_results_is_concise():
    agent = FoodSearchAgent()

    result = agent.format_response(
        FoodSearchResponse(places=[], location="Nha Trang, Việt Nam")
    )

    assert "I could not find matching meal stops" in result


def test_format_response_is_itinerary_friendly():
    agent = FoodSearchAgent()
    response = FoodSearchResponse(
        location="Nha Trang, Việt Nam",
        places=[
            FoodPlace(
                name="Quan Hai San A",
                address="1 Tran Phu",
                rating=4.5,
                price_level="$$",
                type="Seafood",
            )
        ],
    )

    result = agent.format_response(response)

    assert "Meal stop options" in result
    assert "Quan Hai San A" in result
    assert "1 Tran Phu" in result
    assert "4.5" in result
