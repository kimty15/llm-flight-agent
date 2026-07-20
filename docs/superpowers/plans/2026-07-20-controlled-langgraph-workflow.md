# Controlled LangGraph Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the blackbox `create_agent` flow with a small controlled LangGraph workflow for the trip planner.

**Architecture:** Use explicit graph nodes: `analyze_request`, `retrieve_knowledge`, `search_food_if_needed`, and `generate_response`. Keep tools and memory, but make routing and tool calls controlled by our code.

**Tech Stack:** Python 3.10+, LangGraph, LangChain OpenAI, FastAPI, pytest.

## Global Constraints

- Keep `/api/v1/chat` and `/health`.
- Keep per-session memory with a LangGraph checkpointer.
- Keep code simple and readable.
- Do not add booking/payment actions.
- Do not add multi-agent complexity.
- Avoid live API calls in unit tests.

---

## Task 1: Add State And Request Analysis

**Files:**
- Create: `core/state.py`
- Create: `tests/test_graph_nodes.py`

**Interfaces:**
- Produces: `TripState`
- Produces: `analyze_request(state: TripState) -> dict`

## Task 2: Add Controlled Nodes

**Files:**
- Create: `core/nodes.py`
- Modify: `agents/retrieval/retrieval_agent.py`
- Modify: `agents/food_agent/food_search_agent.py`
- Test: `tests/test_graph_nodes.py`

**Interfaces:**
- Produces: `retrieve_knowledge(state: TripState) -> dict`
- Produces: `search_food_if_needed(state: TripState) -> dict`
- Produces: `generate_response(state: TripState) -> dict`

## Task 3: Build The LangGraph Workflow

**Files:**
- Replace: `core/agent_factory.py`
- Modify: `app.py`

**Interfaces:**
- Produces: `build_trip_planner_graph(...)`
- App calls graph with `{"messages": [HumanMessage(...)]}`

## Task 4: Update Docs And Verify

**Files:**
- Modify: `README.md`
- Run: `python -m py_compile ...`
- Run: `python -m pytest tests/test_graph_nodes.py -v` when dependencies are installed.
