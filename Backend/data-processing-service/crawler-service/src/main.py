import os
import time
import logging
from dotenv import load_dotenv
from services.api_client import ImportApiClient
from services.crawler import Crawler

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

  # Crawling interval in seconds
INTERVAL = int(os.getenv('CRAWL_INTERVAL', '5'))
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '20'))

CRAWLED_URLS = []
with open('crawled_urls.txt', 'r') as f:
  CRAWLED_URLS = [line.strip() for line in f.readlines()]

def main():
  
  logger.info("Crawler service started...")
  
  api_client = ImportApiClient()
  crawler = Crawler()

  location_paper_urls = []
  for province_url in CRAWLED_URLS:
    location_paper_urls = location_paper_urls + crawler.crawl_location_paper_urls(province_url)
  
  logger.info(f"Found {len(location_paper_urls)} location paper URLs to crawl.")
  logger.info(location_paper_urls)
  
  def send_batch(jsons):
    result = api_client.batch_import_locations(
      jsons,
      metadata={"import_type": "crawled", "timestamp": time.time()}
    )
    logger.info(f"Successfully sent {len(jsons)} locations. Batch ID: {result.get('request_id')}")
      
  location_jsons = []
  for paper_url in location_paper_urls:
    try:
      location = crawler.crawl_location(paper_url)    
      if location:
        location_jsons.append(location)
      
      if len(location_jsons) >= BATCH_SIZE:
        send_batch(location_jsons)  
        location_jsons = []
      # Wait for the next crawling cycle
      logger.info(f"Waiting {INTERVAL} seconds until next crawl...")
      time.sleep(INTERVAL)
      
    except KeyboardInterrupt:
      logger.info("Shutting down crawler service...")
      break
    except Exception as e:
      logger.error(f"Error in main loop: {str(e)}")
      # Wait a bit before retrying in case of error
      time.sleep(10)

  if len(location_jsons) > 0:
    send_batch(location_jsons)
    location_jsons = []

if __name__ == "__main__":
  main()