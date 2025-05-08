import logging
import asyncio
from typing import Dict, Any
from datetime import datetime
from prometheus_client import Summary
from pydantic import BaseModel

logger = logging.getLogger(__name__)

PROCESSING_TIME = Summary('data_processing_duration_seconds', 'Time spent processing data')

class ProcessorService:
  def __init__(self):
    self.enrichment_tasks = []
    
  @PROCESSING_TIME.time()
  async def process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Process location data and vector embedding, then save to mongodb"""
    new_data = await mongo.insert(data)

    manager.ingest(
        source=merged_text["merged_text"],
        faiss_name=faiss_name,
        _id=new_data["_id"],
    )
    