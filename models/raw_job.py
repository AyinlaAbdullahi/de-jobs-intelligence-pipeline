from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RawJob:
    source: str
    title: str
    company: str
    url: str

    location: Optional[str] = None
    salary_raw: Optional[str] = None
    skills_raw: Optional[str] = None
    description: Optional[str] = None
    posted_at: Optional[datetime] = None
    employment_type: Optional[str] = None
    is_remote: Optional[bool] = None

    scraped_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict:
        return {
            "source": self.source,
            "title": self.title,
            "company": self.company,
            "url": self.url,
            "location": self.location,
            "salary_raw": self.salary_raw,
            "skills_raw": self.skills_raw,
            "description": self.description,
            "posted_at": self.posted_at,
            "employment_type": self.employment_type,
            "is_remote": self.is_remote,
            "scraped_at": self.scraped_at,
        }

    def is_valid(self) -> bool:
        """Minimum viable job: must have title, company and url."""
        return all([self.title, self.company, self.url])