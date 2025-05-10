from dotenv import load_dotenv
import os
from confluent_kafka import Consumer, Producer

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

KAFKA_LOCATION_DATA_TOPIC = os.getenv('KAFKA_LOCATION_DATA_TOPIC', 'location-data')
KAFKA_LOCATION_DATA_DLT_TOPIC = os.getenv('KAFKA_LOCATION_DATA_DLT_TOPIC', 'location-data.dlt')

print(KAFKA_BOOTSTRAP_SERVERS)

def create_consumer() -> Consumer:
  config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'group.id': 'processing-service-group',
    'auto.offset.reset': 'earliest'
  }
  return Consumer(config)

def create_producer() -> Producer:
  config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'client.id': 'processing-service'
  }
  return Producer(config)