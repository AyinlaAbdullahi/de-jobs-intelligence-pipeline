import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import concurrent.futures
from typing import List, Optional
from datetime import datetime, timezone
from models.raw_job import RawJob
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

greenhouse_api = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
greenhouse_job_api = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{job_id}"


def load_target_companies() -> List[str]:
    path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data", "companies", "relevant_greenhouse_companies.json"
    )
    with open(path) as f:
        data = json.load(f)
    return [company["slug"] for company in data]


target_companies = load_target_companies()


class GreenhouseScraper(BaseScraper):

    def __init__(self):
        super().__init__(source_name="greenhouse")

    def scrape(self) -> List[RawJob]:
        jobs = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=15) as executor:
            futures = {
                executor.submit(self._scrape_company, company): company
                for company in target_companies
            }

            for future in concurrent.futures.as_completed(futures):
                company = futures[future]
                try:
                    company_jobs = future.result()
                    jobs.extend(company_jobs)
                except Exception as e:
                    logger.error(f"Failed to scrape {company}: {e}")

        logger.info(f"Greenhouse: {len(jobs)} relevant jobs scraped from {len(target_companies)} companies")
        return jobs

    def _scrape_company(self, company: str) -> List[RawJob]:
        company_jobs = []
        response = self.get(greenhouse_api.format(company=company))

        if not response:
            return company_jobs

        raw_jobs = response.json().get("jobs", [])

        for job in raw_jobs:
            try:
                parsed = self._parse(job, company)
                if parsed and self.is_relevant(parsed.title):
                    full = self._fetch_description(company, job.get("id"))
                    if full:
                        parsed.description = full
                    company_jobs.append(parsed)
            except Exception as e:
                logger.error(f"Failed to parse {company} job: {e}")
                continue

        if company_jobs:
            logger.info(f"{company}: {len(company_jobs)} relevant jobs found")

        return company_jobs

    def _fetch_description(self, company: str, job_id: int) -> str:
        if not job_id:
            return ""
        url = greenhouse_job_api.format(company=company, job_id=job_id)
        response = self.get(url)
        if not response:
            return ""
        data = response.json()
        return data.get("content", "")

    def _parse(self, job: dict, company: str) -> Optional[RawJob]:
        title = (job.get("title") or "").strip()
        url = (job.get("absolute_url") or "").strip()

        if not all([title, url]):
            return None

        real_company_name = (job.get("company_name") or "").strip()
        company_display = real_company_name if real_company_name else company.title()

        location_data = job.get("location", {})
        location = (location_data.get("name") or "") if isinstance(location_data, dict) else ""

        posted_at = None
        raw_date = job.get("updated_at")
        if raw_date:
            try:
                posted_at = datetime.fromisoformat(raw_date.replace("Z", "+00:00"))
            except ValueError:
                pass

        return RawJob(
            source="greenhouse",
            title=title,
            company=company_display,
            url=url,
            location=location,
            posted_at=posted_at,
            is_remote="remote" in location.lower(),
        )