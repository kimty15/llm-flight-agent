"""Langfuse LangChain callback handler for tracing."""

from __future__ import annotations

import os
from typing import Any

from config.settings import Settings, get_settings


def ensure_langfuse_env(settings: Settings | None = None) -> None:
    s = settings or get_settings()
    if s.langfuse_public_key:
        os.environ.setdefault("LANGFUSE_PUBLIC_KEY", s.langfuse_public_key)
    if s.langfuse_secret_key:
        os.environ.setdefault("LANGFUSE_SECRET_KEY", s.langfuse_secret_key)
    if s.langfuse_host:
        os.environ.setdefault("LANGFUSE_HOST", s.langfuse_host)


def build_callback_handler() -> Any | None:
    ensure_langfuse_env()
    s = get_settings()
    if not s.langfuse_public_key or not s.langfuse_secret_key:
        return None
    try:
        from langfuse.langchain import CallbackHandler
    except ImportError:
        return None
    return CallbackHandler()
