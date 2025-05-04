from abc import ABC, abstractmethod
from typing import Annotated, Dict, Any
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from summarization import summarization
#import spacy
from extract_metadata import fetch_from_mongodb
import sys
import argparse
import os
from vector_database import ingest_data_to_vector_db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service")))
print(sys.path)
from vector_store.vectordb import VectorDB
from vector_store.version_manager import get_version_timestamp
#nlp = spacy.load("vi_core_news_lg")
class State(TypedDict):
    messages: Annotated[list, add_messages]
    summary:str
    entities: dict
    location_details: list
    response: str

def summarize(state: State) -> State:
    print("📝 Using Gemini to summarize messages...")
    messages = state.get("messages", [])
    result = summarization(messages)
    state["summary"] = result["summary"]
    state["entities"] = result["entities"]
    print("Entities:", state["entities"])
    return state

def search_vector_db(state: State) -> State:
    print("🔎 Searching with summary:", state["summary"])
    manager = VectorDB()
    global faiss_name    

    try:
        results = manager.search(
            faiss_name=faiss_name,
            query=state['summary'],
            top_k=5,
            threshold=0.7  # Ngưỡng similarity
        )
        # trong search trả về id của document trong mongodb
        location_details = []
        id_strs = []
        for result in results:
            id_strs.append(result["mongo_id"])
        docs = fetch_from_mongodb(id_strs, URL= "vietnamtourism_URL", collection="vietnamtourism_db", document="vietnamtourism_db")
        for doc, result in zip(docs, results):
            print(f"\n🔍 Score: {result['score']:.4f}")
            print(result["content"])            
            #metadata = result["metadata"]
            #name = metadata.get("name", "")  # Chỉ lấy name từ metadata
            #category = metadata.get("category", "").lower()
            #address = metadata.get("address", "")
            
            data = doc.get('data', {})
            name = data.get('name', '')
            address = data.get('address', '')
            category = data.get('category', '').lower()
            description = data.get('discription', '')
            location_details.append({
                "name": name,
                "category": category,
                "address": address,
                "score": result["score"],
                "description": description,
            })
        #state["result"] = locations if locations else ["Phú Quốc", "Đà Lạt", "Vũng Tàu"]
        state["location_details"] = location_details
    except Exception as e:
        print(f"Search error: {str(e)}")
        state["location_details"] = []

    return state

def format_output(state: State) -> State:
    print("🖼️ Formatting response...")
    
    entities = state["entities"]
    locations = entities.get("locations", [])
    features = entities.get("features", [])
    activities = entities.get("activities", [])
    
    reasons = []
    if locations:
        reasons.append(f"Vị trí: {', '.join(locations)}")
    if features:
        reasons.append(f"Đặc điểm: {', '.join(features)}")
    if activities:
        reasons.append(f"Hoạt động: {', '.join(activities)}")
    reason_text = "Dựa trên yêu cầu: " + "; ".join(reasons) + "."

    location_details = state.get("location_details", [])
    if not location_details:
        suggestion_text = "Không tìm thấy địa điểm phù hợp với yêu cầu của bạn."
    else:
        suggestion_text = "Danh sách địa điểm gợi ý:\n"
        for i, detail in enumerate(location_details, 1):
            suggestion_text += (
                f"{i}. {detail['name']} ({detail['description'].capitalize()})\n"
                f"   - Địa chỉ: {detail['address']}\n"
                f"   - Độ phù hợp: {detail['score']:.4f}\n"
            )

    state["response"] = (
        f"{reason_text}\n\n"
        f"{suggestion_text}\n"
        f"Tóm tắt yêu cầu: {state['summary']}"
    )
    return state

parser = argparse.ArgumentParser(description="Run graph.py with a specific faiss_name")
parser.add_argument("--faiss_name", type=str, help="FAISS name to use for the vector database", default=None)
args = parser.parse_args()

if args.faiss_name:
    faiss_name = args.faiss_name
    print(f"Using provided faiss_name: {faiss_name}")
else:
    try:
        with open("faiss_name.txt", "r") as f:
            faiss_name = f.read().strip()
        print(f"Using existing vector database with faiss_name: {faiss_name}")
    except FileNotFoundError:
        print("No existing vector database found. Creating a new one...")
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
    "Tuốn đi đến một nơi nào đó ở Hà Nội.",
    "Tôi nghĩ chúng ta nên đi đến một nơi cổ kính.",
    "tôi nghĩ nên đến khu du lịch",
    #"Nơi nào đó ở xã Ngã Năm cũng hay đấy!"
    #"Vườn cò Tân Long ở Sóc Trăng thì sao nhỉ?",
    #"Tuyệt vời, nghe nói ẩm thực ở đấy rất ngon!",
    #"Ở đó có nhà hàng nào nổi tiếng và đồ ăn rẻ không nhỉ?"
]

final_state = graph.invoke({"messages": messages})
print("\n Final chatbot output:\n", final_state["response"])