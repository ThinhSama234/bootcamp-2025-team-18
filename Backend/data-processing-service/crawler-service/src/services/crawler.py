import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import logging
from typing import Dict, Any, List, Optional
from ratelimit import limits, sleep_and_retry
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import concurrent.futures
from dataclasses import dataclass
from urllib.parse import urljoin

# Configure logging
logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class CrawlerConfig:
  """Configuration for the crawler"""
  max_retries: int = 3
  retry_backoff_factor: float = 0.5
  timeout: int = 10
  max_workers: int = 5
  calls_per_minute: int = 30  # Rate limiting
  user_agent: str = "TourismBot/1.0 (+https://tourism.example.com/bot)"

class Crawler:
  def __init__(self, config: Optional[CrawlerConfig] = None):
    self.config = config or CrawlerConfig()
    self.session = self._setup_session()
    
  def _setup_session(self) -> requests.Session:
    """Configure requests session with retries and timeouts"""
    session = requests.Session()
    retry_strategy = Retry(
      total=self.config.max_retries,
      backoff_factor=self.config.retry_backoff_factor,
      status_forcelist=[429, 500, 502, 503, 504]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update({"User-Agent": self.config.user_agent})
    return session

  @sleep_and_retry
  @limits(calls=CrawlerConfig.calls_per_minute, period=60)
  def _fetch_page(self, url: str) -> Optional[str]:
    """
    Fetch a page with rate limiting and retries
    """
    try:
      response = self.session.get(url, timeout=self.config.timeout)
      response.raise_for_status()
      return response.text
    except requests.RequestException as e:
      logger.error(f"Error fetching {url}: {str(e)}")
      return None

  def _parse_location(self, html: str, source_url: str) -> Optional[Dict[str, Any]]:
    """
    Parse location data from HTML content
    """
    try:
      soup = BeautifulSoup(html, 'html.parser')
      
      # Extract basic information (customize based on target site structure)
      name = soup.find('h1', class_='location-name')
      description = soup.find('div', class_='location-description')
      address = soup.find('div', class_='location-address')
      
      if not name:
        logger.warning(f"No location name found in {source_url}")
        return None
        
      # Extract coordinates (if available)
      coords = self._extract_coordinates(soup)
      
      return {
        "name": name.text.strip(),
        "description": description.text.strip() if description else None,
        "address": address.text.strip() if address else None,
        "coordinates": coords,
        "source_url": source_url,
        "crawled_at": datetime.utcnow().isoformat()
      }
    except Exception as e:
      logger.error(f"Error parsing location from {source_url}: {str(e)}")
      return None

  def _extract_coordinates(self, soup: BeautifulSoup) -> Optional[Dict[str, float]]:
    """Extract coordinates from page if available"""
    try:
      # Look for coordinates in meta tags or map elements
      meta_geo = soup.find('meta', {'name': 'geo.position'})
      if meta_geo:
        lat, lng = meta_geo['content'].split(';')
        return {"lat": float(lat), "lng": float(lng)}
      return None
    except Exception as e:
      logger.error(f"Error extracting coordinates: {str(e)}")
      return None

  def crawl_locations(self, start_urls: List[str]) -> List[Dict[str, Any]]:
    """
    Crawl locations data from various sources.
    Returns a list of location data dictionaries.
    """
    locations = []
    processed_urls = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.max_workers) as executor:
      future_to_url = {
        executor.submit(self._fetch_page, url): url 
        for url in start_urls
      }

      for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
          html = future.result()
          if html and url not in processed_urls:
            location_data = self._parse_location(html, url)
            if location_data:
              locations.append(location_data)
              processed_urls.add(url)
              logger.info(f"Successfully crawled location: {location_data['name']}")
        except Exception as e:
          logger.error(f"Error processing {url}: {str(e)}")

    logger.info(f"Crawling completed. Processed {len(locations)} locations")
    return locations

  def close(self):
    """Clean up resources"""
    self.session.close()