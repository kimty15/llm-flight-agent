"""CLI chat loop using the unified trip planner agent (optional dev utility)."""

from __future__ import annotations

import asyncio

from langchain_core.messages import HumanMessage

from core.agent_factory import build_trip_planner_graph


async def chat_loop() -> None:
    print("Welcome to Nha Trang Trip Planner Agent!")
    print("Ask for Nha Trang itineraries, food stops, attractions, transport, and trip refinements.")
    print("Type 'exit' to end the conversation.")
    print("-" * 50)

    graph = build_trip_planner_graph()
    thread_id = "cli-session"

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == "exit":
            print("\nGoodbye! Thank you for using Nha Trang Trip Planner Agent.")
            break

        try:
            result = await graph.ainvoke(
                {"messages": [HumanMessage(content=user_input)]},
                config={"configurable": {"thread_id": thread_id}},
            )
            msgs = result.get("messages", [])
            last = msgs[-1] if msgs else None
            text = getattr(last, "content", str(last)) if last else ""
            print("\nAssistant:", text)
        except Exception as e:
            print(f"\nError: {e}")


if __name__ == "__main__":
    asyncio.run(chat_loop())
