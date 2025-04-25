from abc import ABC, abstractmethod
from typing import Annotated, Dict, Any
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from summarization import summarization

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service/vector_store")))
print(sys.path)
from vectordb import VectorDB
from version_manager import get_version_timestamp
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
    print("🔎 Tìm kiếm theo summary:", state["summary"])
    manager = VectorDB()
    mock_data = {
        "name": "Trảng Cỏ Bù Lạch",
        "address": "Thôn 7, xã Đồng Nai, huyện Bù Đăng, tỉnh Bình Phước, Việt Nam",
        "description": "Trảng Cỏ Bù Lạch là một thảo nguyên rộng khoảng 500 ha...",
        "image_url": "https://tse3.mm.bing.net/th?id=OIP.w3Gngig-IiMeqb4bw0NTUwHaFD&pid=Api"
    }    
    name_encode = mock_data['name']
    address_encode = mock_data['address']
    description_encode = mock_data['description']
    faiss_name = get_version_timestamp()
    merge_text = name_encode + " " + address_encode + " " + description_encode
    print(merge_text)
    try:
        result = manager.ingest(
            source=merge_text,
            faiss_name=faiss_name,
        )
        print(f"Data ingested successfully.")
    except Exception as e:
        print(f"❌ Error processing {merge_text}: {str(e)}")

    # input: summary
    # search
    print("🔎 Tìm kiếm theo summary:")
    try:
        results = manager.search(
            faiss_name=faiss_name,
            query=state['summary'],
            top_k=1,
            threshold=0.6  # Ngưỡng similarity
        )
        
        for result in results:
            print(f"\n🔍 Score: {result["score"]:.4f}")
            print(result["content"])
            print(result["source"])
        print(1)
    except Exception as e:
        print(f"Search error: {str(e)}")
    state["result"] = results
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
        "Bình Phước thì sao nhỉ?",
        "Thật đúng lúc, tôi đang muốn leo núi."
]

final_state = graph.invoke({"messages": messages})
print("\n Final chatbot output:\n", final_state["response"])