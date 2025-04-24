from abc import ABC, abstractmethod
from typing import Annotated, Dict, Any
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from summarization import summarization

class State(TypedDict):
    messages: Annotated[list, add_messages]
    summary:str
    entities: list
    result: list
    response: str

def summarize(state: State) -> State:
    print("📝 Using Gemini to summarize messages...")
    messages = state.get("messages", [])
    result = summarization(messages)
    state["summary"] = result["summary"]
    state["entities"] = result["entities"]
    return state

def search_vector_db(state: State) -> State:
    print("🔎 Tìm kiếm theo entities:", state["entities"])
    state["result"] = ["Phú Quốc", "Đà Lạt", "Vũng Tàu"]
    return state

def format_output(state: State) -> State:
    print("🖼️ Formatting response...")
    state["response"] = f"Gợi ý du lịch: {', '.join(state['result'])}\n(Tóm tắt: {state['summary']})"
    return state

builder = StateGraph(State)
builder.add_node("Summarize", RunnableLambda(summarize))
builder.add_node("Search", RunnableLambda(search_vector_db))
builder.add_node("Format", RunnableLambda(format_output))

builder.add_edge("Summarize", "Search")
builder.add_edge("Search", "Format")
builder.add_edge("Format", END)

builder.set_entry_point("Summarize")

graph = builder.compile()

messages = [
    "Tôi muốn đi du lịch đến một nơi có nhiều cảnh đẹp thiên nhiên, không khí trong lành và yên tĩnh.",
        "Còn tôi thì muốn đi đến một nơi nào đó ở miền Nam.",
        "Tôi nghĩ chúng ta nên đi đến một nơi có đồi núi.",
        "Đà Lạt thì sao nhỉ?",
        "Thật đúng lúc, tôi đang muốn leo núi."
]

final_state = graph.invoke({"messages": messages})
print("\n Final chatbot output:\n", final_state["response"])