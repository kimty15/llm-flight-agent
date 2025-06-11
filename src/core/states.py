"""State definitions for the conversation flow."""

from typing import TypedDict, Annotated, Literal
from pydantic import BaseModel, Field
from langgraph.graph import add_messages

class State(TypedDict):
    """State definition for the conversation flow."""
    messages: Annotated[list, add_messages]
    message_type: str

class Router(BaseModel):
    """Router model for determining message handling."""
    message_type: Literal["food_search_agent", "retrieval_agent", "ignore"] = Field(
        ...,
        description="The type of agent to route the question to food_search_agent or retrieval_agent or ignore"
    ) 