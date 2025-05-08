import os
from confluent_kafka import Consumer

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_LOCATION_DATA_TOPIC = os.getenv('KAFKA_LOCATION_DATA_TOPIC', 'location-data')

def create_consumer() -> Consumer:
  config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'processing-service-group',
    'auto.offset.reset': 'earliest'
  }
  return Consumer(config)
