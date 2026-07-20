from __future__ import annotations

from typing import Annotated, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TripState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    session_id: str
    user_id: str
    request_id: str
    mode: str
    needs_food: bool
    knowledge_context: str
    food_context: str
