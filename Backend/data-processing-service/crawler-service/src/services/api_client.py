import os
import requests
import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class ImportApiClient:
  def __init__(self):
    self.base_url = os.getenv('INGEST_SERVICE_URL', 'http://localhost:8000')
    self.session = requests.Session()

  def import_location(self, location_data: Dict[str, Any], metadata: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Send a single location to the import API
    """
    response = self.session.post(
      f"{self.base_url}/api/v1/import",
      json={
        "source": "crawler",
        "data": location_data,
        "metadata": metadata or {"import_type": "crawled"}
      }
    )
    response.raise_for_status()
    return response.json()

  def batch_import_locations(
    self,
    locations: List[Dict[str, Any]],
    metadata: Dict[str, Any] = None
  ) -> Dict[str, Any]:
    """
    Send a batch of locations to the import API
    """
    try:
      response = self.session.post(
        f"{self.base_url}/api/v1/import/batch",
        json={
          "source": "crawler",
          "items": locations,
          "metadata": metadata or {}
        }
      )
      response.raise_for_status()
      return response.json()
      
    except requests.RequestException as e:
      logger.error(f"Error sending batch to import API: {str(e)}")
      raise

  def close(self):
    """Clean up resources"""
    self.session.close()