import re
import logging
from bs4 import BeautifulSoup
from db.connection import get_session
from db.models import RawJob as RawJobDB, Job as JobDB

logger = logging.getLogger(__name__)


def is_accessible_from_nigeria(location: str) -> bool:
    if not location or location.strip() == "":
        return True

    location_lower = location.lower().strip()

    # Reject only clearly onsite jobs
    onsite_signals = [
        "onsite", "on-site", "on site", "in office",
        "in-office", "hybrid", "headquarters", "hq",
    ]
    for signal in onsite_signals:
        if signal in location_lower:
            return False

    return True


def parse_salary(salary_raw: str) -> tuple:
    if not salary_raw:
        return None, None, "USD"

    salary_raw = salary_raw.replace(",", "").replace(" ", "")

    currency = "USD"
    if "£" in salary_raw or "GBP" in salary_raw:
        currency = "GBP"
    elif "€" in salary_raw or "EUR" in salary_raw:
        currency = "EUR"
    elif "CAD" in salary_raw:
        currency = "CAD"

    multipliers = {"k": 1000, "K": 1000, "m": 1000000, "M": 1000000}
    for suffix, mult in multipliers.items():
        salary_raw = re.sub(
            rf'(\d+\.?\d*){suffix}',
            lambda m: str(int(float(m.group(1)) * mult)),
            salary_raw
        )

    numbers = re.findall(r'\d+', salary_raw)
    numbers = [int(n) for n in numbers if 10000 <= int(n) <= 1000000]

    if len(numbers) >= 2:
        return min(numbers), max(numbers), currency
    elif len(numbers) == 1:
        return numbers[0], numbers[0], currency

    return None, None, currency


def strip_html(text: str) -> str:
    if not text:
        return ""
    return BeautifulSoup(text, "html.parser").get_text(separator=" ", strip=True)


def infer_experience_level(title: str) -> str:
    title_lower = title.lower()
    if any(w in title_lower for w in ["intern", "internship"]):
        return "INTERN"
    if any(w in title_lower for w in ["junior", "jr.", "jr ", "entry", "associate", "graduate", "new grad"]):
        return "JUNIOR"
    if any(w in title_lower for w in ["senior", "sr.", "sr ", "lead", "principal", "staff", "head of"]):
        return "SENIOR"
    if any(w in title_lower for w in ["manager", "director", "vp ", "vice president", "chief"]):
        return "MANAGER"
    return "MID"


def infer_beginner_friendly(title: str, description: str) -> bool:
    text = f"{title} {description}".lower()
    signals = [
        "entry level", "junior", "no experience", "new grad",
        "recent graduate", "0-1 year", "0-2 year", "internship",
        "associate", "beginner", "early career",
    ]
    return any(s in text for s in signals)


def clean_jobs() -> dict:
    accepted = 0
    rejected = 0
    errors = 0

    with get_session() as session:
        raw_jobs = session.query(RawJobDB).filter(
            RawJobDB.is_processed == False
        ).all()

        logger.info(f"Cleaning {len(raw_jobs)} unprocessed jobs")

        for raw in raw_jobs:
            try:
                if not is_accessible_from_nigeria(raw.location):
                    raw.is_processed = True
                    rejected += 1
                    continue

                salary_min, salary_max, currency = parse_salary(raw.salary_raw or "")
                description_clean = strip_html(raw.description or "")
                experience_level = infer_experience_level(raw.title or "")
                beginner_friendly = infer_beginner_friendly(
                    raw.title or "", description_clean
                )

                existing = session.query(JobDB).filter(
                    JobDB.job_hash == raw.job_hash
                ).first()

                if existing:
                    raw.is_processed = True
                    accepted += 1
                    continue

                job = JobDB(
                    job_hash=raw.job_hash,
                    raw_job_id=raw.id,
                    title=raw.title,
                    company_name=raw.company,
                    location=raw.location,
                    is_remote=True,
                    source=raw.source,
                    url=raw.url,
                    salary_min=salary_min,
                    salary_max=salary_max,
                    salary_currency=currency,
                    experience_level=experience_level,
                    beginner_friendly=beginner_friendly,
                    posted_at=raw.posted_at,
                    scraped_at=raw.scraped_at,
                )

                session.add(job)
                raw.is_processed = True
                accepted += 1

            except Exception as e:
                logger.error(f"Error cleaning job {raw.title}: {e}")
                errors += 1
                continue

    logger.info(f"Cleaner: {accepted} accepted, {rejected} rejected, {errors} errors")
    return {"accepted": accepted, "rejected": rejected, "errors": errors}