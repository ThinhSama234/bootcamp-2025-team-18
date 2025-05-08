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
    try:
      self.enrichment_tasks = [
        self._enrich_with_weather(data),
        self._enrich_with_reviews(data),
        self._enrich_with_photos(data)
      ]
      
      results = await asyncio.gather(*self.enrichment_tasks, return_exceptions=True)
      
      enriched_data = data.copy()
      for result in results:
        if isinstance(result, dict):
          enriched_data.update(result)
      
      enriched_data['processed_at'] = datetime.now().isoformat()
      logger.info(f"Successfully processed data for location: {data.get('name')}")
      
      return enriched_data
      
    except Exception as e:
      logger.error(f"Error processing data: {str(e)}")
      raise

  async def _enrich_with_weather(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Add weather information if coordinates are available"""
    try:
      coords = data.get('coordinates')
      if coords and coords.get('lat') and coords.get('lng'):
        # Simulate weather API call
        await asyncio.sleep(0.1)
        return {
          'weather': {
            'temperature': 20,
            'conditions': 'sunny'
          }
        }
      return {}
    except Exception as e:
      logger.error(f"Error enriching with weather: {str(e)}")
      return {}

  async def _enrich_with_reviews(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Add review information"""
    try:
      # Simulate reviews API call
      await asyncio.sleep(0.1)
      return {
        'reviews': {
          'average_rating': 4.5,
          'total_reviews': 100
        }
      }
    except Exception as e:
      logger.error(f"Error enriching with reviews: {str(e)}")
      return {}

  async def _enrich_with_photos(self, data: Dict[str, Any]) -> Dict[str, Any]:
    """Add additional photos if available"""
    try:
      # Simulate photos API call
      await asyncio.sleep(0.1)
      return {
        'additional_photos': [
          'https://example.com/location1.jpg',
          'https://example.com/location2.jpg'
        ]
      }
    except Exception as e:
      logger.error(f"Error enriching with photos: {str(e)}")
      return {}