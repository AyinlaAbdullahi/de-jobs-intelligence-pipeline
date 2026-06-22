from typing import List
from datetime import datetime, timezone
from models.raw_job import RawJob
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

REMOTIVE_API = "https://remotive.com/api/remote-jobs"

TARGET_CATEGORIES = [
    "data",
    "software-development",
    "devops",
    "engineering",
]


class RemotiveScraper(BaseScraper):

    def __init__(self):
        super().__init__(source_name="remotive")

    def scrape(self) -> List[RawJob]:
        jobs = []

        for category in TARGET_CATEGORIES:
            logger.info(f"Scraping Remotive category: {category}")
            response = self.get(f"{REMOTIVE_API}?category={category}")

            if not response:
                logger.warning(f"No response for category: {category}")
                continue

            data = response.json()
            raw_jobs = data.get("jobs", [])
            logger.info(f"Found {len(raw_jobs)} jobs in {category}")

            for job in raw_jobs:
                try:
                    parsed = self._parse(job)
                    if parsed and self.is_relevant(parsed.title):
                        jobs.append(parsed)
                except Exception as e:
                    logger.error(f"Failed to parse job: {e}")
                    continue

        logger.info(f"Remotive: {len(jobs)} relevant jobs scraped")
        return jobs

    def _parse(self, job: dict) -> RawJob | None:
        title = (job.get("title") or "").strip()
        company = (job.get("company_name") or "").strip()
        url = (job.get("url") or "").strip()

        if not all([title, company, url]):
            return None

        posted_at = None
        raw_date = job.get("publication_date")
        if raw_date:
            try:
                posted_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            except ValueError:
                pass

        return RawJob(
            source="remotive",
            title=title,
            company=company,
            url=url,
            location=job.get("candidate_required_location", ""),
            salary_raw=job.get("salary", ""),
            skills_raw=", ".join(job.get("tags", [])),
            description=job.get("description", ""),
            posted_at=posted_at,
            is_remote=True,
        )