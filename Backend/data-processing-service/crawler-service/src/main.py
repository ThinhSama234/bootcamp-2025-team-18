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

def main():
  api_client = ImportApiClient()
  crawler = Crawler()
  
  # Crawling interval in seconds (5 minutes)
  interval = int(os.getenv('CRAWL_INTERVAL', '300'))
  
  logger.info("Crawler service started...")
  
  while True:
    try:
      # Get locations from crawler
      locations = [] #crawler.crawl_locations(['https://example.com'])
      
      if locations:
        # Send batch of crawled locations
        result = api_client.batch_import_locations(
          locations,
          metadata={"import_type": "crawled", "timestamp": time.time()}
        )
        logger.info(f"Successfully sent {len(locations)} locations. Batch ID: {result.get('request_id')}")
      
      # Wait for the next crawling cycle
      logger.info(f"Waiting {interval} seconds until next crawl...")
      time.sleep(interval)
      
    except KeyboardInterrupt:
      logger.info("Shutting down crawler service...")
      break
    except Exception as e:
      logger.error(f"Error in main loop: {str(e)}")
      # Wait a bit before retrying in case of error
      time.sleep(10)

if __name__ == "__main__":
  main()