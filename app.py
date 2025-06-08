from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import asyncio
from typing import List, Optional
from core.graph import TravelAssistantGraph
from logger import Logger

app = FastAPI(
    title="Nha Trang Tourism Assistant API",
    description="API for the Nha Trang Tourism Assistant chatbot",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize logger
logger = Logger().get_logger()

# Initialize graph
graph = TravelAssistantGraph()
app_graph = graph.create_graph()

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    messages: List[ChatMessage]

# Store chat states
chat_states = {}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Get or create session
        session_id = request.session_id or datetime.now().strftime("%Y%m%d_%H%M%S")
        logger.info(f"Processing request for session {session_id}")

        # Get or initialize state
        if session_id not in chat_states:
            chat_states[session_id] = {
                "messages": [],
                "message_type": None
            }
        
        state = chat_states[session_id]
        
        # Add user message to state
        state["messages"].append({"role": "user", "content": request.message})
        logger.info(f"Session {session_id} - User message: {request.message}")

        # Process message
        result = await app_graph.ainvoke(
            state,
            config={"configurable": {"thread_id": session_id}}
        )

        # Update state
        chat_states[session_id] = result
        
        # Get assistant response
        assistant_message = result["messages"][-1].content
        logger.info(f"Session {session_id} - Assistant response: {assistant_message}")

        # Convert messages to ChatMessage format
        messages = [ChatMessage(role=msg.type, content=msg.content) 
                   for msg in result["messages"]]

        return ChatResponse(
            response=assistant_message,
            session_id=session_id,
            messages=messages
        )

    except Exception as e:
        error_msg = str(e)
        logger.error(f"Session {session_id} - Error: {error_msg}", exc_info=True)
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)