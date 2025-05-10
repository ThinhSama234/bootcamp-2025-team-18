import logging
import asyncio
from typing import Dict, Any
from datetime import datetime
#from prometheus_client import Summary
from pydantic import BaseModel
from data_interface import MongoDB
from vectorDB import VectorDB
logger = logging.getLogger(__name__)

#PROCESSING_TIME = Summary('data_processing_duration_seconds', 'Time spent processing data')

class ProcessorService:
  def __init__(self, db: MongoDB, db_vector: MongoDB):
    self.enrichment_tasks = []
    self.db = db
    self.db_vector = db_vector
    self.embedding_queue = asyncio.Queue(maxsize= 100)
    self.faiss_name = datetime.now().strftime("%Y%m%d_%H%M%S")
    self.manager = VectorDB()
    self.running = True
    self._start_index_worker()  # Khởi động worker để index batch
  #@PROCESSING_TIME.time()
  async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process location data and vector embedding, then save to mongodb"""
    try: 
      # lưu vào mongo
      new_data = await self.db.save_record(data)  # Lưu vào db thông thường
      print(f"✅ Saved to MongoDB: {new_data["_id"]}")
      _id = new_data.get("_id")
      data = new_data.get('data', {})
      name = data.get('name', '')
      address = data.get('address', '')
      description = data.get('description', '')
      category = data.get('category', '')
      merged_text = f"{name} {address} {category} {description}".strip()
      print(f"Processing: {merged_text[:50]}...")
      embedding = self.manager.embed_texts([merged_text])[0].tolist()
      queue_item = {
        "type": "location",
        "embedding": embedding,
        "mongo_id": str(_id),
      }
      await self.embedding_queue.put(queue_item)
      print(f"✅ Queued embedding for _id: {new_data["_id"]}")
      #In số document hiện tại trong locations và locations_vector
      loc_count = await self.db.collection.count_documents({})
      vec_count = await self.db_vector.collection.count_documents({})
      print(f"Current document count - locations: {loc_count}, locations_vector: {vec_count}")
      return new_data
    except Exception as e:
      print(f"❌ Error processing data: {str(e)}")
      return data
  def _start_index_worker(self):
    """Worker để index batch từ queue định kỳ."""
    async def index_worker():
      while self.running:
        try:
          batch = []
          timeout = 5.0
          while len(batch)<50 and not self.embedding_queue.empty():
            item = await asyncio.wait_for(self.embedding_queue.get(), timeout=timeout)
            batch.append(item)
            self.embedding_queue.task_done()
          if batch:
            embeddings = [item["embedding"] for item in batch]
            mongo_ids = [item["mongo_id"] for item in batch] 
            await self.db_vector.insert_many([
                            {"_id": mongo_id, "embedding": embedding}
                            for mongo_id, embedding in zip(mongo_ids, embeddings)])
            print(f"✅ Indexed batch of {len(batch)} items")
            # In số document hiện tại sau khi index
            vec_count = await self.db_vector.collection.count_documents({})
            print(f"Updated document count in locations_vector: {vec_count}")
        except asyncio.TimeoutError:
            continue  # Chờ thêm nếu queue trống
        except Exception as e:
            print(f"❌ Error indexing batch: {str(e)}")
        await asyncio.sleep(1)  # Chờ 1 giây trước khi kiểm tra lại
    asyncio.create_task(index_worker())
  
  async def shutdown(self):
    """Dừng worker khi service shutdown."""
    self.running = False
    await asyncio.sleep(1)  # Chờ worker hoàn thành
    # Đóng kết nối MongoDB
    self.db.client.close()
    self.db_vector.client.close()
    print("✅ Closed MongoDB connections")

# Hàm main để test
async def main():
    uri = "mongodb+srv://truongthinh2301:tpuNNUBTBxrgOm1a@cluster0.dlrf4cw.mongodb.net/"
    db = MongoDB(uri, database="travel_db", collection="locations")
    db_vector = MongoDB(uri, database="travel_db", collection="locations_vector")

    # Khởi tạo service
    processor_service = ProcessorService(db, db_vector)

    # Mô phỏng dữ liệu để kiểm tra
    # Mô phỏng dữ liệu để kiểm tra
    records = [
        {
            "type": "location",
            "data": {
                "name": "Location A",
                "address": "123 Street, City",
                "description": "A great place to visit.",
                "category": "Tourism"
            }
        },
        {
            "type": "location",
            "data": {
                "name": "Location B",
                "address": "456 Avenue, Town",
                "description": "Another nice spot.",
                "category": "Nature"
            }
        }
    ]
    for record in records:
        result = await processor_service.process_data(record)
        print(f"Processed result: {result}")
        await asyncio.sleep(1)  # Giả lập delay giữa các tài liệu

    # Đợi một chút để worker xử lý
    await asyncio.sleep(10)

    # Shutdown
    await processor_service.shutdown()

# Chạy main
if __name__ == "__main__":
    asyncio.run(main())