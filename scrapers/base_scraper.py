from typing import Optional
from abc import ABC, abstractmethod
from typing import List
from models.raw_job import RawJob
import requests
import time
import logging
from config.settings import settings

logger = logging.getLogger(__name__)


class BaseScraper(ABC):

    def __init__(self, source_name: str):
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        })

    @abstractmethod
    def scrape(self) -> List[RawJob]:
        #Every scraper must implement this method.
        pass

    def get(self, url: str) -> Optional[requests.Response]:
        #Makes an HTTP GET request with retries and delay.
        for attempt in range(settings.max_retries):
            try:
                time.sleep(settings.request_delay)
                response = self.session.get(url, timeout=settings.request_timeout)
                response.raise_for_status()
                return response
            except requests.RequestException as e:
                logger.warning(f"Attempt {attempt + 1} failed for {url}: {e}")
                if attempt == settings.max_retries - 1:
                    logger.error(f"All retries failed for {url}")
                    return None

    def is_relevant(self, title: str) -> bool:
        #Checks if a job title matches our target roles.
        title_lower = title.lower()
        return any(role in title_lower for role in settings.target_roles)