import os
import json
import logging
import signal
from dotenv import load_dotenv
from datetime import datetime
from prometheus_client import start_http_server, Counter, Gauge
from marshmallow import ValidationError
from confluent_kafka import Consumer, TopicPartition

from config.kafka_config import KAFKA_LOCATION_DATA_TOPIC, create_consumer
from data_interface import MongoDB
from models.location_data import MessageSchema, LocationSchema
from .processor import ProcessorService
from config.db_config import TRAVELDB_URL

load_dotenv()

PORT = int(os.getenv('PORT', 8000))

logger = logging.getLogger(__name__)

MESSAGES_PROCESSED = Counter('messages_processed_total', 'Total messages processed', ['status'])
PROCESSING_TIME = Gauge('message_processing_seconds', 'Time spent processing messages')
CONSUMER_LAG = Gauge('consumer_lag', 'Consumer lag in messages')

location_db = MongoDB(TRAVELDB_URL, database="travel_db", collection="locations")
vector_db = MongoDB(TRAVELDB_URL, database="travel_db", collection="locations_vector")

class DataProcessor:
  def __init__(self):
    self.consumer: Consumer = create_consumer()
    self.processor = ProcessorService(location_db, vector_db)
    self.location_schema = LocationSchema()
    self.running = True
    self.setup_signal_handlers()

  async def process_message(self, msg) -> bool:
    try:
      start_time = datetime.now()
      
      value = json.loads(msg.value().decode('utf-8'))
      validated_data = await self.location_schema.load(value.get('data', {}))
      
      await self.processor.process_data(validated_data)
      
      # Update metrics
      processing_time = (datetime.now() - start_time).total_seconds()
      PROCESSING_TIME.set(processing_time)
      MESSAGES_PROCESSED.labels(status='success').inc()
      
      return True
      
    except json.JSONDecodeError as e:
      logger.error(f"Invalid JSON in message: {str(e)}")
      MESSAGES_PROCESSED.labels(status='json_error').inc()
    except ValidationError as e:
      logger.error(f"Data validation failed: {str(e)}")
      MESSAGES_PROCESSED.labels(status='validation_error').inc()
    except Exception as e:
      logger.error(f"Error processing message: {str(e)}")
      MESSAGES_PROCESSED.labels(status='error').inc()
    
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