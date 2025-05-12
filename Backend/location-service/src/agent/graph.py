from typing import Annotated, Dict, Tuple, List
from typing_extensions import TypedDict

from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableLambda

#import spacy
from agent.summarization import summarization
from database.vectordb import VectorDB
from database.data_interface import MongoDB

from config.config import TRAVELDB_URL

#nlp = spacy.load("vi_core_news_lg")
class State(TypedDict):
    messages: Annotated[list, add_messages]
    summary:str
    entities: dict
    location_details: list
    response: List[Dict]
class Graph:
    def __init__(self, db: MongoDB, db_vector: MongoDB):
        self.db = db
        self.db_vector = db_vector
        return
    
    def summarize(self, state: State) -> State:
        """ Tóm tắt các tin nhắn và trích xuất thực thể. """
        print("📝 Using Gemini to summarize messages...")
        messages = state.get("messages", [])
        result = summarization(messages)
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

    def search_vector_db(self, db_vector: MongoDB, state: State, k) -> State:
        """Tìm kiếm trong vector database dựa trên tóm tắt."""
        print("🔎 Searching with summary:", state["summary"])
        manager = VectorDB()
        try:
            results = manager.search(
                db= self.db,
                db_vector = self.db_vector,
                query_text=state['summary'],
                entities=state["entities"],
                top_k=k,
                threshold=0.2
            )
            # trong search trả về id của document trong mongodb
            id_strs = [result["mongo_id"] for result in results]
            state["location_details"] = id_strs
            print(f"🔍 Found mongo_ids: {id_strs}")
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
            state["response"] = [{"message": "Không tìm thấy địa điểm phù hợp với yêu cầu của bạn."}]
        else:
            state["response"] = [
                {
                    "index": i + 1,
                    "name": detail["name"],
                    "category": detail["category"].capitalize(),
                    "address": detail["address"],
                    "description": detail["description"],
                    "score": detail["score"],
                    "_id": str(detail["_id"])
                }
                for i, detail in enumerate(location_details)
            ]
            state["response"].insert(0, {"reason": reason_text})
            state["response"].append({"summary": f"Tóm tắt yêu cầu: {state['summary']}"})
        return state
    def process_messages(self, db_vector: MongoDB, messages: list[str], k) -> Tuple[list, str]:
        """Xử lý messages và trả về location_details và response."""
        initial_state = {"messages": messages}
        state = self.summarize(initial_state)
        state = self.search_vector_db(db_vector,state, k)
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
    uri = TRAVELDB_URL
    db = MongoDB(uri, database="travel_db", collection="locations")
    db_vector = MongoDB(uri, database="travel_db", collection="locations_vector")
    graph = Graph()
    location_details, response = graph.process_messages(db_vector, messages)
    print("\nLocation Details:\n", location_details)
    print("\nFinal chatbot output:\n", response)
