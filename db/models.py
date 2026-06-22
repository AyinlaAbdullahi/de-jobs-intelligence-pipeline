from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Integer, Float, Boolean,
    DateTime, Text, JSON, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

def utcnow():
    return datetime.now(timezone.utc)


class RawJob(Base):
    __tablename__ = "raw_jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_hash = Column(String(64), unique=True, nullable=False)
    source = Column(String(50), nullable=False)
    title = Column(String(255))
    company = Column(String(255))
    location =  Column(Text)
    salary_raw = Column(String(255))
    skills_raw = Column(Text)
    description = Column(Text)
    url = Column(String(500))
    posted_at = Column(DateTime)
    scraped_at = Column(DateTime, default=utcnow)
    is_processed = Column(Boolean, default=False)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), unique=True, nullable=False)
    domain = Column(String(255))
    is_verified = Column(Boolean, default=False)
    employee_count = Column(String(50))
    trust_score = Column(Float, default=0.0)
    domain_age_days = Column(Integer)
    linkedin_exists = Column(Boolean)
    ats_platform = Column(String(100))
    scam_flags = Column(JSON, default=list)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    jobs = relationship("Job", back_populates="company_rel")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_hash = Column(String(64), unique=True, nullable=False)
    raw_job_id = Column(Integer, ForeignKey("raw_jobs.id"))
    company_id = Column(Integer, ForeignKey("companies.id"))
    title = Column(String(255))
    company_name = Column(String(255))
    location = Column(String(255))
    is_remote = Column(Boolean, default=False)
    employment_type = Column(String(50))
    experience_level = Column(String(50))
    visa_sponsorship = Column(Boolean, default=False)
    timezone_requirement = Column(String(100))
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String(10))
    required_skills = Column(JSON, default=list)
    preferred_skills = Column(JSON, default=list)
    trust_score = Column(Float, default=0.0)
    trust_classification = Column(String(50))
    resume_match_score = Column(Float, default=0.0)
    ranking_score = Column(Float, default=0.0)
    beginner_friendly = Column(Boolean, default=False)
    scam_signals = Column(JSON, default=list)
    duplicate_confidence = Column(Float, default=0.0)
    original_job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    rejection_reason = Column(String(255))
    is_active = Column(Boolean, default=True)
    source = Column(String(50))
    url = Column(String(500))
    posted_at = Column(DateTime)
    scraped_at = Column(DateTime)
    created_at = Column(DateTime, default=utcnow)
    updated_at = Column(DateTime, default=utcnow, onupdate=utcnow)

    company_rel = relationship("Company", back_populates="jobs")


class PipelineLog(Base):
    __tablename__ = "pipeline_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    run_id = Column(String(100), unique=True)
    dag_id = Column(String(100))
    status = Column(String(50))
    rows_scraped = Column(Integer, default=0)
    rows_loaded = Column(Integer, default=0)
    rows_rejected = Column(Integer, default=0)
    rows_deduplicated = Column(Integer, default=0)
    rejection_reasons = Column(JSON, default=dict)
    error_message = Column(Text)
    started_at = Column(DateTime, default=utcnow)
    finished_at = Column(DateTime)


class TrustRecord(Base):
    __tablename__ = "trust_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_hash = Column(String(64), nullable=False)
    trust_score = Column(Float)
    classification = Column(String(50))
    scam_signals = Column(JSON, default=list)
    scored_at = Column(DateTime, default=utcnow)


class TrendSnapshot(Base):
    __tablename__ = "trend_snapshots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    snapshot_date = Column(DateTime, nullable=False)
    skill = Column(String(100))
    role = Column(String(100))
    job_count = Column(Integer, default=0)
    avg_salary = Column(Float)
    remote_count = Column(Integer, default=0)

    __table_args__ = (
        UniqueConstraint("snapshot_date", "skill", "role", name="uq_trend_snapshot"),
    )