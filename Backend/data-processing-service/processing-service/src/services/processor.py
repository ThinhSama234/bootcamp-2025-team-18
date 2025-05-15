import logging
import asyncio
from typing import Dict, Any
from prometheus_client import Summary

from config.db_config import TRAVELDB_URL
from database.data_interface import MongoDB
from database.vectorDB import VectorDB

logger = logging.getLogger(__name__)

PROCESSING_TIME = Summary('data_processing_duration_seconds', 'Time spent processing data')

class ProcessorService:
  def __init__(self, db: MongoDB, db_vector: MongoDB):
    self.db = db
    self.db_vector = db_vector
    self.embedding_queue = asyncio.Queue(maxsize= 100)
    self.manager = VectorDB()
    self.running = True
    self._start_index_worker()  # Khởi động worker để index batch
  
  @PROCESSING_TIME.time()
  async def process_data(self, message: Dict[str, Any]) -> Dict[str, Any]:
    """Process location data and vector embedding, then save to mongodb"""
    try:
      lat = message.get("data").get("latitude")
      lon = message.get("data").get("longitude")
      if message.get("data").get("latitude") and message.get("data").get("longitude"):
        message['location'] = {
          "type": "Point",
          "coordinates": [float(lat), float(lon)]
        }
      new_data = await self.db.save_record(message)
      logger.info(f"✅ Saved to MongoDB: {new_data['_id']}")
      logger.info(new_data)

      _id = new_data.get("_id")
      data = new_data.get('data', {})

      name = data.get('name', '')
      address = data.get('address', '')
      description = data.get('description', '')
      category = data.get('category', '')

      merged_text = f"{name} {address} {category} {description}".strip()
      logger.info(f"Processing: {merged_text[:50]}...")

      embedding = self.manager.embed_texts([merged_text])[0].tolist()
      queue_item = {
        "type": new_data["type"],
        "embedding": embedding,
        "id_mongo": str(_id),
      }
      logger.info(f"Embedding created: {queue_item}...")
      await self.embedding_queue.put(queue_item)
      logger.info(f"✅ Queued embedding for _id: {new_data['_id']}")
      
      #In số document hiện tại trong locations và locations_vector
      loc_count = await self.db.collection.count_documents({})
      vec_count = await self.db_vector.collection.count_documents({})
      logger.info(f"Current document count - locations: {loc_count}, locations_vector: {vec_count}")
    except Exception as e:
      logger.info(f"❌ Error processing data: {str(e)}")
    
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
            mongo_ids = [item["id_mongo"] for item in batch] 
            await self.db_vector.insert_many([
                            {"id_mongo": id_mongo, "embedding": embedding}
                            for id_mongo, embedding in zip(mongo_ids, embeddings)])
            logger.info(f"✅ Indexed batch of {len(batch)} items")
            # In số document hiện tại sau khi index
            vec_count = await self.db_vector.collection.count_documents({})
            logger.info(f"Updated document count in locations_vector: {vec_count}")
        except asyncio.TimeoutError:
          continue  # Chờ thêm nếu queue trống
        except Exception as e:
          logger.info(f"❌ Error indexing batch: {str(e)}")
        await asyncio.sleep(1)  # Chờ 1 giây trước khi kiểm tra lại
    loop = asyncio.get_running_loop()
    loop.create_task(index_worker())
  
  async def shutdown(self):
    """Dừng worker khi service shutdown."""
    self.running = False
    await asyncio.sleep(1)  # Chờ worker hoàn thành
    # Đóng kết nối MongoDB
    self.db.client.close()
    self.db_vector.client.close()
    logger.info("✅ Closed MongoDB connections")




# Hàm main để test
async def main():
    uri = TRAVELDB_URL
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
        await processor_service.process_data(record)
        await asyncio.sleep(1)  # Giả lập delay giữa các tài liệu

    # Đợi một chút để worker xử lý
    await asyncio.sleep(10)

    # Shutdown
    await processor_service.shutdown()

# Chạy main
if __name__ == "__main__":
    asyncio.run(main())