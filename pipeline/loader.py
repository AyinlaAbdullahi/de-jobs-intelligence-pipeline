import hashlib
import logging
from typing import List
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import insert
from models.raw_job import RawJob
from db.connection import get_session
from db.models import RawJob as RawJobDB

logger = logging.getLogger(__name__)


def generate_job_hash(title: str, company: str, url: str) -> str:
    raw = f"{title.lower().strip()}{company.lower().strip()}{url.strip()}"
    return hashlib.sha256(raw.encode()).hexdigest()


def load_raw_jobs(jobs: List[RawJob]) -> dict:
    inserted = 0
    updated = 0
    skipped = 0

    for job in jobs:
        try:
            if not job.is_valid():
                skipped += 1
                continue

            job_hash = generate_job_hash(job.title, job.company, job.url)

            with get_session() as session:
                stmt = insert(RawJobDB).values(
                    job_hash=job_hash,
                    source=job.source,
                    title=job.title,
                    company=job.company,
                    location=(job.location or "")[:500],
                    salary_raw=job.salary_raw,
                    skills_raw=job.skills_raw,
                    description=job.description,
                    url=job.url,
                    posted_at=job.posted_at,
                    scraped_at=datetime.now(timezone.utc),
                    is_processed=False,
                ).on_conflict_do_update(
                    index_elements=["job_hash"],
                    set_={
                        "scraped_at": datetime.now(timezone.utc),
                        "is_processed": False,
                    }
                )

                result = session.execute(stmt)

                if result.rowcount == 1:
                    inserted += 1
                else:
                    updated += 1

        except Exception as e:
            logger.error(f"Failed to load job {job.title}: {e}")
            skipped += 1
            continue

    logger.info(f"Loader: {inserted} inserted, {updated} updated, {skipped} skipped")
    return {"inserted": inserted, "updated": updated, "skipped": skipped}