import asyncio
import logging

from database.data_interface import MongoDB
from config.db_config import TRAVELDB_URL

from services.processor import ProcessorService
from services.data_processor import DataProcessor

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
  # Initialize databases within the running event loop
  location_db = MongoDB(TRAVELDB_URL, database="travel_db", collection="locations")
  vector_db = MongoDB(TRAVELDB_URL, database="travel_db", collection="locations_vector")
  
  # Create 2dsphere index if it does not already exist
  index_name = "location_2dsphere"
  existing_indexes = await location_db.collection.index_information()
  if index_name not in existing_indexes:
    await location_db.collection.create_index(
      [("location", "2dsphere")],
      name=index_name
    )
  
  processor_service = ProcessorService(location_db, vector_db)
  processor = DataProcessor(processor_service)
  await processor.run()

if __name__ == "__main__":
  asyncio.run(main())