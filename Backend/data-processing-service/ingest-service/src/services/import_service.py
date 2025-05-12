import json
import uuid
from typing import Any, Dict, List, Optional
import logging

from config.kafka_config import KAFKA_LOCATION_DATA_TOPIC, create_producer

logger = logging.getLogger(__name__)

class ImportService:
  def __init__(self):
    self.producer = create_producer()
    self.producer.poll(0)  # Trigger any delivery report callbacks from previous produce calls
    self.producer.flush()
    logger.info("Kafka producer initialized")

  def _delivery_report(self, err, msg):
    if err is not None:
      logger.error(f'Message delivery failed: {err}')
    else:
      logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

  def send_to_kafka(
    self,
    source: str,
    type: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
  ) -> str:
    request_id = str(uuid.uuid4())
    message = {
      'request_id': request_id,
      'source': source,
      'type': type,
      'data': data,
      'metadata': metadata or {}
    }
    
    try:
      self.producer.produce(
        KAFKA_LOCATION_DATA_TOPIC, 
        json.dumps(message).encode('utf-8'),
        callback=self._delivery_report
      )
      self.producer.flush()
      logger.info(f"Message sent successfully to Kafka. Request ID: {request_id}")
      return request_id
    except Exception as e:
      logger.error(f"Error sending message to Kafka: {str(e)}")
      raise

  def batch_send_to_kafka(
    self,
    items: List[Dict[str, Any]],
  ) -> str:
    batch_id = str(uuid.uuid4())
    
    try:
      for item in items:
        message = {
          'batch_id': batch_id,
          'request_id': str(uuid.uuid4()),
          'source': item.get('source', 'crawler'),
          'data': item.get('data'),
          'type': item.get('type', 'location'),
          'metadata': item.get('metadata', {})
        }
        self.producer.produce(
          KAFKA_LOCATION_DATA_TOPIC, 
          json.dumps(message).encode('utf-8'),
          callback=self._delivery_report
        )
      
      self.producer.flush()
      logger.info(f"Batch sent successfully to Kafka. Batch ID: {batch_id}")
      return batch_id
    except Exception as e:
      logger.error(f"Error sending batch to Kafka: {str(e)}")
      raise