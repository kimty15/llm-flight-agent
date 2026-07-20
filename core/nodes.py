from __future__ import annotations

from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from agents.food_agent.food_search_agent import FoodSearchAgent
from agents.retrieval.retrieval_agent import RetrievalAgent
from config.settings import Settings, get_settings
from core.state import TripState
from prompts.prompt_template import RESPONSE_PROMPT

PLAN_KEYWORDS = (
    "plan",
    "itinerary",
    "trip",
    "schedule",
    "lịch trình",
    "kế hoạch",
    "du lịch",
    "ngày",
)

FOOD_KEYWORDS = (
    "food",
    "restaurant",
    "cafe",
    "coffee",
    "lunch",
    "dinner",
    "breakfast",
    "eat",
    "ăn",
    "quán",
    "cà phê",
    "cafe",
    "bữa",
    "hải sản",
)

retrieval_agent = RetrievalAgent()
food_agent = FoodSearchAgent()


def latest_user_text(state: TripState) -> str:
    messages = state.get("messages", [])
    for message in reversed(messages):
        if getattr(message, "type", "") == "human":
            return str(getattr(message, "content", ""))
    return ""


def has_keyword(text: str, keywords: tuple[str, ...]) -> bool:
    lowered = text.lower()
    return any(keyword in lowered for keyword in keywords)


def analyze_request(state: TripState) -> dict:
    text = latest_user_text(state)
    needs_food = has_keyword(text, FOOD_KEYWORDS)
    wants_plan = has_keyword(text, PLAN_KEYWORDS) or needs_food
    return {
        "mode": "plan" if wants_plan else "qa",
        "needs_food": needs_food,
    }


def retrieve_knowledge(state: TripState) -> dict:
    question = latest_user_text(state)
    if not question:
        return {"knowledge_context": ""}
    try:
        return {"knowledge_context": retrieval_agent.run(question)}
    except Exception as e:
        return {"knowledge_context": f"Knowledge lookup unavailable: {type(e).__name__}"}


def search_food_if_needed(state: TripState) -> dict:
    if not state.get("needs_food"):
        return {"food_context": ""}

    query = latest_user_text(state)
    try:
        parsed = food_agent.parse_food_query(query)
        if not parsed.is_nha_trang and parsed.location:
            return {"food_context": "Meal-stop search is limited to Nha Trang."}
        result = food_agent.search_food_places(parsed.query, parsed.location)
        return {"food_context": food_agent.format_response(result)}
    except Exception as e:
        return {"food_context": f"Meal-stop search unavailable: {type(e).__name__}"}


def generate_response(state: TripState, settings: Settings | None = None) -> dict:
    s = settings or get_settings()
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", RESPONSE_PROMPT),
            (
                "user",
                "Mode: {mode}\n\nUser request:\n{request}\n\nKnowledge context:\n{knowledge_context}\n\nFood context:\n{food_context}",
            ),
        ]
    )
    llm = ChatOpenAI(model=s.llm_model, temperature=s.temperature)
    chain = prompt | llm
    response = chain.invoke(
        {
            "mode": state.get("mode", "qa"),
            "request": latest_user_text(state),
            "knowledge_context": state.get("knowledge_context", ""),
            "food_context": state.get("food_context", ""),
        }
    )
    return {"messages": [AIMessage(content=str(response.content))]}
