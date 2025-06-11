"""Chat API routes."""

from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException
from src.api.schemas import ChatRequest, ChatResponse, ChatMessage
from src.core.graph import TravelAssistantGraph

router = APIRouter(tags=["chat"])

# Initialize graph once
graph = TravelAssistantGraph()
app_graph = graph.create_graph()

# Store chat states (in production, use Redis or database)
chat_states: Dict[str, Dict[str, Any]] = {}

@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Handle chat requests."""
    try:
        # Get or create session
        session_id = request.session_id or datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get or initialize state
        if session_id not in chat_states:
            chat_states[session_id] = {
                "messages": [],
                "message_type": None
            }
        
        state = chat_states[session_id]
        
        # Add user message to state
        state["messages"].append({"role": "user", "content": request.message})

        # Process message
        result = await app_graph.ainvoke(
            state,
            config={"configurable": {"thread_id": session_id}}
        )

        # Update state
        chat_states[session_id] = result
        
        # Get assistant response
        assistant_message = result["messages"][-1].content

        # Convert messages to ChatMessage format
        messages = [
            ChatMessage(role=msg.type, content=msg.content) 
            for msg in result["messages"]
        ]

        return ChatResponse(
            response=assistant_message,
            session_id=session_id,
            messages=messages
        )

    except Exception as e:
        error_msg = str(e)
        raise HTTPException(status_code=500, detail=error_msg) 