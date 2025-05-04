from abc import ABC, abstractmethod
from typing import Annotated, Dict, Any, Tuple
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda
from summarization import summarization
import spacy

import sys
import argparse
import os
from vector_database import ingest_data_to_vector_db
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data-service/vector_store")))
print(sys.path)
from vectordb import VectorDB
from version_manager import get_version_timestamp
#nlp = spacy.load("vi_core_news_lg")
class State(TypedDict):
    messages: Annotated[list, add_messages]
    summary:str
    entities: dict
    location_details: list
    response: str

class Graph:
    def __init__(self, faiss_name: str = None):
        self.faiss_name = self._get_or_create_faiss_name(faiss_name)

    def _get_or_create_faiss_name(self, faiss_name: str = None) -> str:
        """Lấy faiss_name từ argument, file, hoặc tạo mới nếu không có."""
        # Kiểm tra thư mục hiện tại
        current_dir = os.getcwd()
        print(f"Current working directory: {current_dir}")
        faiss_file_path = os.path.join(current_dir, "faiss_name.txt")
        print(f"Looking for faiss_name.txt at: {faiss_file_path}")

        # Nếu faiss_name được truyền vào
        if faiss_name:
            print(f"Using provided faiss_name: {faiss_name}")
            return faiss_name
        
        parser = argparse.ArgumentParser(description="Run graph.py with a specific faiss_name")
        parser.add_argument("--faiss_name", type=str, help="FAISS name to use for the vector database", default=None)
        args = parser.parse_args()

        if args.faiss_name:
            faiss_name = args.faiss_name
            print(f"Using provided faiss_name: {faiss_name}")
        # Kiểm tra file faiss_name.txt
        try:
            with open(faiss_file_path, "r") as f:
                faiss_name = f.read().strip()
            print(f"Using existing vector database with faiss_name: {faiss_name}")
            return faiss_name
        except FileNotFoundError:
            print("No existing vector database found. Creating a new one...")
            faiss_name = ingest_data_to_vector_db()
            # Lưu faiss_name vào file
            with open(faiss_file_path, "w") as f:
                f.write(faiss_name)
            print(f"Saved faiss_name to {faiss_file_path}: {faiss_name}")
            return faiss_name
    
    def summarize(self, state: State) -> State:
        """Tóm tắt các tin nhắn và trích xuất thực thể."""
        print("📝 Using Gemini to summarize messages...")
        messages = state.get("messages", [])
        if not messages:
            print("⚠️ No messages provided for summarization.")
            state["summary"] = ""
            state["entities"] = {}
        else:
            result = summarization(messages)
            state["summary"] = result.get("summary", "")
            state["entities"] = result.get("entities", {})
        print("Entities:", state["entities"])
        return state
    
    def search_vector_db(self, state: State) -> State:
        """Tìm kiếm trong vector database dựa trên tóm tắt."""
        print("🔎 Searching with summary:", state["summary"])
        manager = VectorDB()

        try:
            results = manager.search(
                faiss_name=self.faiss_name,
                query=state["summary"],
                top_k=5,
                threshold=0.6  # Ngưỡng similarity
            )
            location_details = [
                {
                    "_id": result["metadata"].get("_id", ""),  # Lấy _id từ metadata
                    "name": result["metadata"].get("name", ""),
                    "category": result["metadata"].get("category", "").lower(),
                    "address": result["metadata"].get("address", ""),
                    "score": result["score"]
                }
                for result in results
            ]
            state["location_details"] = location_details
            for detail in location_details:
                print(f"🔍 Name: {detail['name']}, ID: {detail['_id']}, Score: {detail['score']:.4f}")
        except Exception as e:
            print(f"Search error: {str(e)}")
            state["location_details"] = []

        return state
    
    def format_output(self, state: State) -> State:
        """Định dạng đầu ra dựa trên entities và location_details."""
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
        reason_text = "Dựa trên yêu cầu: " + "; ".join(reasons) + "." if reasons else "Dựa trên yêu cầu của bạn."

        location_details = state.get("location_details", [])
        if not location_details:
            suggestion_text = "Không tìm thấy địa điểm phù hợp với yêu cầu của bạn."
        else:
            suggestion_text = "Danh sách địa điểm gợi ý:\n"
            for i, detail in enumerate(location_details, 1):
                suggestion_text += (
                    f"{i}. {detail['name']} ({detail['category'].capitalize()})\n"
                    f"   - Địa chỉ: {detail['address']}\n"
                    f"   - Độ phù hợp: {detail['score']:.4f}\n"
                )

        state["response"] = (
            f"{reason_text}\n\n"
            f"{suggestion_text}\n"
            f"Tóm tắt yêu cầu: {state['summary']}"
        )
        return state
    
    def process_messages(self, messages: list[str]) -> Tuple[list, str]:
        """Xử lý messages và trả về location_details và response."""
        initial_state = {"messages": messages}
        state = self.summarize(initial_state)
        state = self.search_vector_db(state)
        state = self.format_output(state)
        return state["location_details"], state["response"]
    
    def run(self, state: State) -> State:
        """Chạy toàn bộ graph."""
        builder = StateGraph(State)
        builder.add_node("Summarize", RunnableLambda(self.summarize))
        builder.add_node("Search", RunnableLambda(self.search_vector_db))
        builder.add_node("Format", RunnableLambda(self.format_output))

        builder.add_edge("Summarize", "Search")
        builder.add_edge("Search", "Format")
        builder.add_edge("Format", END)

        builder.set_entry_point("Summarize")
        graph = builder.compile()
        return graph.invoke(state)

if __name__ == "__main__":
    messages = [
        "Tôi nghĩ chúng ta nên đi đến một nơi có đồi núi.",
    ]

    graph = Graph()
    location_details, response = graph.process_messages(messages)
    print("\nLocation Details:\n", location_details)
    print("\nFinal chatbot output:\n", response)