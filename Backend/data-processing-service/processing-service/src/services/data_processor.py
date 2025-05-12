import os
import json
import logging
import signal
from typing import Any
from dotenv import load_dotenv
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge
from marshmallow import ValidationError
from confluent_kafka import TopicPartition
from dotenv import load_dotenv
load_dotenv()

from models.location_data import MessageSchema
from .processor import ProcessorService

from config.kafka_config import KAFKA_LOCATION_DATA_DLT_TOPIC, KAFKA_LOCATION_DATA_TOPIC, create_consumer, create_producer

load_dotenv()

PORT = int(os.getenv('PORT', 8000))

logger = logging.getLogger(__name__)

MESSAGES_PROCESSED = Counter('messages_processed_total', 'Total messages processed', ['status'])
PROCESSING_TIME = Gauge('message_processing_seconds', 'Time spent processing messages')
CONSUMER_LAG = Gauge('consumer_lag', 'Consumer lag in messages')

class DataProcessor:
  def __init__(self, processor_service: ProcessorService):
    self.message_schema = MessageSchema()
    self.consumer = create_consumer()
    self.dlt_producer = create_producer()

    self.processor = processor_service
    self.running = True
    self.setup_signal_handlers()

  async def close(self):
    self.running = False
    await self.processor.shutdown()
    self.consumer.close()
    self.dlt_producer.flush()

  def _send_to_dlt(self, error_type: str, original_message: Any, errors: str):
    dlt_message = {
      'error': error_type,
      'original_message': original_message.value().decode('utf-8'),
      'errors': errors,
      'timestamp': datetime.now().isoformat()
    }
    self.dlt_producer.produce(
      KAFKA_LOCATION_DATA_DLT_TOPIC,
      json.dumps(dlt_message).encode('utf-8')
    )
    logger.error(f"Sent message to DLT: {dlt_message}")

  async def process_message(self, msg) -> bool:
    try:
      start_time = datetime.now()
      
      value = json.loads(msg.value().decode('utf-8'))
      validated_data = self.message_schema.load(value)
      
      await self.processor.process_data(validated_data)
      
      # Update metrics
      processing_time = (datetime.now() - start_time).total_seconds()
      PROCESSING_TIME.set(processing_time)
      MESSAGES_PROCESSED.labels(status='success').inc()
      
      return True
    except json.JSONDecodeError as e:
      logger.error(f"Invalid JSON in message: {str(e)}")
      MESSAGES_PROCESSED.labels(status='json_error').inc()
      self._send_to_dlt('json_error', msg, str(e))

    except ValidationError as e:
      logger.error(f"Data validation failed: {str(e)}")
      MESSAGES_PROCESSED.labels(status='validation_error').inc()
      self._send_to_dlt('validation_error', msg, str(e))

    except Exception as e:
      logger.error(f"Error processing message: {str(e)}")
      MESSAGES_PROCESSED.labels(status='error').inc()
      self._send_to_dlt('exception', msg, str(e))    

    return False

  async def run(self):
    try:
      self.consumer.subscribe([KAFKA_LOCATION_DATA_TOPIC])
      logger.info(f"Subscribed to topic: {KAFKA_LOCATION_DATA_TOPIC}")
      
      # Start metrics server
      start_http_server(PORT)
      logger.info(f"Metrics server started on port {PORT}")
      
      while self.running:
        msg = self.consumer.poll(1.0)
        
        if msg is None:
          continue
        if msg.error():
          logger.error(f"Consumer error: {msg.error()}")
          continue
        
        # Update lag metric
        if msg.topic() == KAFKA_LOCATION_DATA_TOPIC:
          tp = TopicPartition(msg.topic(), msg.partition())
          position = self.consumer.position([tp])
          if position and len(position) > 0:
            CONSUMER_LAG.set(position[0].offset)
        
        # Process message
        await self.process_message(msg)
        
    except Exception as e:
      logger.error(f"Fatal error in processing loop: {str(e)}")
      raise
    finally:
      logger.info("Shutting down consumer...")
      self.consumer.close()
      
  def setup_signal_handlers(self):
    for sig in (signal.SIGTERM, signal.SIGINT):
      signal.signal(sig, self.shutdown_handler)

  def shutdown_handler(self, signum, frame):
    logger.info("Received shutdown signal, cleaning up...")
    self.running = False