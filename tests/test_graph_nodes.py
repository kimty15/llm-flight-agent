from langchain_core.messages import HumanMessage

from core.nodes import analyze_request, search_food_if_needed


def test_analyze_request_detects_trip_planning():
    state = {"messages": [HumanMessage(content="Lập lịch trình 2 ngày ở Nha Trang")]}

    result = analyze_request(state)

    assert result["mode"] == "plan"
    assert result["needs_food"] is False


def test_analyze_request_detects_food_need():
    state = {"messages": [HumanMessage(content="Gợi ý bữa trưa gần Tháp Bà")]}

    result = analyze_request(state)

    assert result["mode"] == "plan"
    assert result["needs_food"] is True


def test_search_food_skips_when_not_needed():
    state = {
        "messages": [HumanMessage(content="Nha Trang có bãi biển nào đẹp?")],
        "needs_food": False,
    }

    result = search_food_if_needed(state)

    assert result == {"food_context": ""}
