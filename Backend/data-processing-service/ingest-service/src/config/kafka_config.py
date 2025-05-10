import os
from dotenv import load_dotenv
from confluent_kafka import Producer

load_dotenv()

KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')

KAFKA_LOCATION_DATA_TOPIC = os.getenv('KAFKA_LOCATION_DATA_TOPIC', 'location-data')

def create_producer():
  config = {
    'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
    'client.id': 'ingest-service'
  }
  return Producer(config)
