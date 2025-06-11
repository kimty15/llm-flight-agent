"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ChatMessage(BaseModel):
    """Chat message model."""
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    """Chat request model."""
    message: str = Field(..., description="User message")
    session_id: Optional[str] = Field(None, description="Session identifier")

class ChatResponse(BaseModel):
    """Chat response model."""
    response: str = Field(..., description="Assistant response")
    session_id: str = Field(..., description="Session identifier")
    messages: List[ChatMessage] = Field(..., description="Conversation history")

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Response timestamp") 