from typing import List
from datetime import datetime, timezone
from models.raw_job import RawJob
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

HIMALAYAS_API = "https://himalayas.app/jobs/api"


class HimalayasScraper(BaseScraper):

    def __init__(self):
        super().__init__(source_name="himalayas")

    def scrape(self) -> List[RawJob]:
        jobs = []
        offset = 0
        limit = 100
        max_jobs = 10000

        while offset < max_jobs:
            logger.info(f"Scraping Himalayas offset: {offset}")
            response = self.get(f"{HIMALAYAS_API}?limit={limit}&offset={offset}")

            if not response:
                break

            data = response.json()
            raw_jobs = data.get("jobs", [])

            if not raw_jobs:
                break

            for job in raw_jobs:
                try:
                    parsed = self._parse(job)
                    if parsed and self.is_relevant(parsed.title):
                        jobs.append(parsed)
                except Exception as e:
                    logger.error(f"Failed to parse job: {e}")
                    continue

            offset += limit

        seen = set()
        unique_jobs = []
        for job in jobs:
            if job.url not in seen:
                seen.add(job.url)
                unique_jobs.append(job)

        logger.info(f"Himalayas: {len(unique_jobs)} relevant jobs from {offset} scanned")
        return unique_jobs

    def _parse(self, job: dict) -> RawJob | None:
        title = (job.get("title") or "").strip()
        company = (job.get("companyName") or "").strip()
        url = (job.get("applicationLink") or job.get("guid") or "").strip()

        if not all([title, company, url]):
            return None

        posted_at = None
        raw_date = job.get("pubDate")
        if raw_date:
            try:
                posted_at = datetime.fromtimestamp(int(raw_date), tz=timezone.utc)
            except (ValueError, TypeError):
                pass

        salary_raw = ""
        if job.get("minSalary") and job.get("maxSalary"):
            salary_raw = f"{job['minSalary']}-{job['maxSalary']} {job.get('currency', 'USD')}"

        location_restrictions = job.get("locationRestrictions", [])
        location = ", ".join(location_restrictions) if location_restrictions else "Worldwide"

        return RawJob(
            source="himalayas",
            title=title,
            company=company,
            url=url,
            location=location,
            salary_raw=salary_raw,
            skills_raw=", ".join(job.get("categories", [])),
            description=job.get("description", ""),
            employment_type=job.get("employmentType", ""),
            posted_at=posted_at,
            is_remote=True,
        )