from typing import List, Optional
from datetime import datetime, timezone
from models.raw_job import RawJob
from scrapers.base_scraper import BaseScraper
import logging

logger = logging.getLogger(__name__)

greenhouse_api = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
greenhouse_job_api = "https://boards-api.greenhouse.io/v1/boards/{company}/jobs/{job_id}"

target_companies = [
    "reddit", "pinterest", "lyft", "scaleai", "airbnb",
    "stripe", "databricks", "anthropic", "twilio", "brex",
    "robinhood", "block", "figma", "clickhouse", "mongodb",
    "elastic", "hightouch", "datadog", "yugabyte", "collibra",
    "intercom", "klaviyo", "samsara", "verkada", "gusto",
    "chime", "nubank", "instacart", "adyen", "monzo",
    "asana", "peloton", "marqeta", "airtable", "lattice",
    "n26", "upwork", "sendbird", "mixpanel", "paystack",
    "zscaler", "cloudflare", "fastly", "amplitude", "braze",
    "iterable", "attentive", "postscript", "discord", "dropbox",
    "gitlab", "circleci", "fivetran", "sisense", "dremio",
    "starburst", "imply", "algolia", "mercury", "current",
    "alpaca", "gemini", "payoneer", "c6bank", "inter",
    "greenhouse", "justworks", "remote", "oura", "newrelic",
    "cortex", "pagerduty", "planetscale", "beam", "labelbox",
    "tanium", "sonicwall", "okta", "buzzfeed", "insider",
    "axios", "zocdoc", "vercel", "netlify", "make", "workato",
    "postman", "launchdarkly", "dataiku", "sas", "anaplan",
    "calendly", "pandadoc", "veracode", "beyondtrust", "doximity",
    "faire", "taskrabbit", "fetch", "bark", "branch", "orchard",
    "knock", "webflow", "glide", "salesloft", "zuora",
    "aftership", "narvar", "loop", "squarespace", "myfitnesspal",
    "calm", "talkspace", "cerebral", "comet", "toloka",
    "remotasks", "highnote", "lithic", "sezzle", "affirm",
    "crisp", "consensys", "fireblocks", "ripple", "bitgo",
    "spacex", "relativity", "astranis", "spire", "waymo",
    "motional", "duolingo", "coursera", "udacity", "skillsoft",
    "carta", "twitch", "rumble", "affinity", "pendo", "userflow",
    "oddball", "fingerprint", "fleetio", "tucows",
    "knack", "godaddy", "customerio", "ebury",
]


class GreenhouseScraper(BaseScraper):

    def __init__(self):
        super().__init__(source_name="greenhouse")

    def scrape(self) -> List[RawJob]:
        jobs = []

        for company in target_companies:
            logger.info(f"Scraping Greenhouse: {company}")
            response = self.get(greenhouse_api.format(company=company))

            if not response:
                continue

            raw_jobs = response.json().get("jobs", [])
            logger.info(f"{company}: {len(raw_jobs)} total jobs")

            for job in raw_jobs:
                try:
                    parsed = self._parse(job, company)
                    if parsed and self.is_relevant(parsed.title):
                        full = self._fetch_description(company, job.get("id"))
                        if full:
                            parsed.description = full
                        jobs.append(parsed)
                except Exception as e:
                    logger.error(f"Failed to parse {company} job: {e}")
                    continue

        logger.info(f"Greenhouse: {len(jobs)} relevant jobs scraped")
        return jobs

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
            company=company.title(),
            url=url,
            location=location,
            posted_at=posted_at,
            is_remote="remote" in location.lower(),
        )