from typing import List, Optional
from datetime import datetime, timezone
from models.raw_job import RawJob
from scrapers.base_scraper import BaseScraper
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

wfhng_api = "https://workfromhome.ng/wp-json/wp/v2/job_listing"


class WFHNGScraper(BaseScraper):

    def __init__(self):
        super().__init__(source_name="wfhng")

    def scrape(self) -> List[RawJob]:
        jobs = []
        page = 1
        max_pages = 50  # fetch up to 50 pages × 20 jobs = 1000 jobs max

        while page <= max_pages:
            logger.info(f"Scraping WorkFromHome.ng page {page}")
            response = self.get(f"{wfhng_api}?per_page=20&page={page}")

            if not response:
                break

            data = response.json()

            if not data:
                break

            for job in data:
                try:
                    parsed = self._parse(job)
                    if parsed and self.is_relevant(parsed.title):
                        jobs.append(parsed)
                except Exception as e:
                    logger.error(f"Failed to parse job: {e}")
                    continue

            page += 1

        seen = set()
        unique_jobs = []
        for job in jobs:
            if job.url not in seen:
                seen.add(job.url)
                unique_jobs.append(job)

        logger.info(f"WorkFromHome.ng: {len(unique_jobs)} relevant jobs scraped")
        return unique_jobs

    def _parse(self, job: dict) -> Optional[RawJob]:
        title = job.get("title", {}).get("rendered", "").strip()
        title = BeautifulSoup(title, "html.parser").get_text()

        metas = job.get("metas", {})
        url = metas.get("_job_apply_url", "") or job.get("link", "")

        if not all([title, url]):
            return None

        description = BeautifulSoup(
            job.get("content", {}).get("rendered", ""),
            "html.parser"
        ).get_text(separator=" ", strip=True)

        salary_raw = metas.get("_job_salary", "") or ""

        posted_at = None
        raw_date = job.get("date_gmt")
        if raw_date:
            try:
                posted_at = datetime.fromisoformat(raw_date + "+00:00")
            except ValueError:
                pass

        company = ""
        category = metas.get("_job_category", {})
        if isinstance(category, dict):
            category_name = ", ".join(category.values())
        else:
            category_name = ""

        return RawJob(
            source="wfhng",
            title=title,
            company=company or "unknown",
            url=url,
            location="Remote (Africa friendly)",
            salary_raw=salary_raw,
            description=description,
            skills_raw=category_name,
            posted_at=posted_at,
            is_remote=True,
        )