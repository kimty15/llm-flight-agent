from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Any

from fastapi import APIRouter, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import AIMessage, HumanMessage
from pydantic import BaseModel, Field

from config.settings import get_settings
from core.agent_factory import build_trip_planner_graph
from logger import Logger
from observability.langfuse_setup import build_callback_handler
from safety.guardrails import moderate_openai_if_enabled, validate_message

logger = Logger().get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    app.state.agent = build_trip_planner_graph(settings=settings)
    app.state.settings = settings
    logger.info("Trip planner graph compiled")
    yield


def _cors_origins() -> list[str]:
    raw = get_settings().cors_origins
    if raw == "*":
        return ["*"]
    return [o.strip() for o in raw.split(",") if o.strip()]


app = FastAPI(
    title="Nha Trang Trip Planner Agent API",
    description="API for an agentic Nha Trang trip planner with memory, RAG, food-search tools, guardrails, and observability.",
    version="2.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter()


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str | None = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    messages: list[ChatMessage]
    request_id: str
    guardrail_flags: dict[str, Any] = Field(default_factory=dict)


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    request.state.request_id = rid
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response


def new_session_id() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def build_metadata(session_id: str, request_id: str, body: ChatRequest, flags: Any) -> dict[str, Any]:
    metadata: dict[str, Any] = {
        "langfuse_session_id": session_id,
        "request_id": request_id,
        "possible_injection": flags.possible_injection,
    }
    if body.user_id:
        metadata["langfuse_user_id"] = body.user_id
    return metadata


def assistant_text(messages: list[Any]) -> str:
    if not messages:
        return ""
    last = messages[-1]
    if isinstance(last, AIMessage):
        return str(last.content)
    return str(getattr(last, "content", last))


def to_chat_messages(messages: list[Any]) -> list[ChatMessage]:
    chat_messages: list[ChatMessage] = []
    for msg in messages:
        role = getattr(msg, "type", "unknown")
        if role == "human":
            role = "user"
        elif role == "ai":
            role = "assistant"

        content = getattr(msg, "content", str(msg))
        if isinstance(content, list):
            content = str(content)
        chat_messages.append(ChatMessage(role=role, content=content))
    return chat_messages


@api_router.post("/chat", response_model=ChatResponse)
async def chat_v1(request: Request, body: ChatRequest):
    settings = request.app.state.settings
    session_id = body.session_id or new_session_id()
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))

    gr = validate_message(body.message, settings)
    if not gr.ok:
        raise HTTPException(status_code=400, detail=gr.message)

    mod = await moderate_openai_if_enabled(gr.trimmed or body.message, settings)
    if not mod.ok:
        raise HTTPException(status_code=400, detail=mod.message)

    lf_handler = build_callback_handler()
    callbacks = [lf_handler] if lf_handler else []

    graph = request.app.state.agent
    try:
        result = await graph.ainvoke(
            {
                "messages": [HumanMessage(content=body.message)],
                "session_id": session_id,
                "user_id": body.user_id or "",
                "request_id": request_id,
            },
            config={
                "configurable": {"thread_id": session_id},
                "callbacks": callbacks,
                "metadata": build_metadata(session_id, request_id, body, mod),
            },
        )
    except Exception as e:
        logger.exception("Agent error session=%s", session_id)
        raise HTTPException(
            status_code=503,
            detail="The assistant is temporarily unavailable. Please try again.",
        ) from e

    messages_out = result.get("messages", [])

    flags = {
        "possible_injection": mod.possible_injection,
        "moderation_flagged": mod.moderation_flagged,
        "mode": result.get("mode"),
        "needs_food": result.get("needs_food"),
    }

    return ChatResponse(
        response=assistant_text(messages_out),
        session_id=session_id,
        messages=to_chat_messages(messages_out),
        request_id=request_id,
        guardrail_flags=flags,
    )


app.include_router(api_router, prefix=get_settings().api_prefix)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
