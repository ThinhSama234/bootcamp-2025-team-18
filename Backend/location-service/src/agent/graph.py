from abc import ABC, abstractmethod
from typing import Annotated, Dict, Any
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from summarization import summarization

import sys
import os
from vector_database import ingest_data_to_vector_db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service/vector_store")))
print(sys.path)
from vectordb import VectorDB
from version_manager import get_version_timestamp
class State(TypedDict):
    messages: Annotated[list, add_messages]
    summary:str
    entities: dict
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
    print("🔎 Searching with summary:", state["summary"])
    manager = VectorDB()
    global faiss_name    

    try:
        results = manager.search(
            faiss_name=faiss_name,
            query=state['summary'],
            top_k=3,
            threshold=0.9  # Ngưỡng similarity
        )
        
        locations = []
        for result in results:
            print(f"\n🔍 Score: {result['score']:.4f}")
            print(result["content"])
            print(result["source"])
            content = result["content"]
            name = content.split(" Thôn ")[0] if " Thôn " in content else content.split(" ")[0]
            if name not in locations:
                locations.append(name)
        state["result"] = locations if locations else ["Phú Quốc", "Đà Lạt", "Vũng Tàu"]
    except Exception as e:
        print(f"Search error: {str(e)}")
        state["result"] = ["Phú Quốc", "Đà Lạt", "Vũng Tàu"]

    return state

def format_output(state: State) -> State:
    print("🖼️ Formatting response...")
    
    entities = state["entities"]
    locations = entities.get("locations", [])
    features = entities.get("features", [])
    activities = entities.get("actitvies", [])

    reasons = []
    if locations:
        reasons.append(f"Vị trí: {', '.join(locations)}")
    if features:
        reasons.append(f"Đặc điểm: {', '.join(features)}")
    if activities:
        reasons.append(f"Hoạt động thú vị: {', '.join(activities)})")
    
    reason_text = "Dựa trên yêu cầu: " + ";".join(reasons) + "."

    if not state["result"]:
        suggestion_text = "Không tìm thấy địa điểm phù hợp với yêu cầu của bạn."
    else:
        suggestion_text = "Danh sách địa điểm gợi ý:\n"
        for i, location in enumerate(state["result"], 1):
            suggestion_text += f"{i}. {location}\n"

    state["response"] = (
        f"{reason_text}\n\n"
        f"{suggestion_text}\n"
        f"Tóm tắt yêu cầu: {state['summary']}"
    )
    return state


faiss_name = ingest_data_to_vector_db()

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
        "Quảng Nam thì sao nhỉ?",
        "Thật đúng lúc, tôi đang muốn leo núi."
]

final_state = graph.invoke({"messages": messages})
print("\n Final chatbot output:\n", final_state["response"])