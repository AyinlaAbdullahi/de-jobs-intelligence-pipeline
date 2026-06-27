import logging
from db.connection import get_session
from db.models import Job as JobDB, RawJob as RawJobDB

logger = logging.getLogger(__name__)

your_skills = [
    "python", "sql", "airflow", "dbt", "docker",
    "postgresql", "postgres", "snowflake", "streamlit",
    "pandas", "git", "github", "azure", "databricks",
    "spark", "pyspark", "etl", "elt", "pipeline",
]

priority_skills = [
    "python", "sql", "airflow", "dbt", "spark", "azure",
]

experience_scores = {
    "intern":  20,
    "junior":  30,
    "mid":     25,
    "senior":  10,
    "manager": 0,
}


def score_skills(description: str, title: str) -> int:
    if not description:
        return 0

    text = f"{title} {description}".lower()
    score = 0

    for skill in your_skills:
        if skill in text:
            score += 2
            if skill in priority_skills:
                score += 3

    return min(score, 40)


def score_experience(experience_level: str) -> int:
    level = (experience_level or "mid").lower()
    return experience_scores.get(level, 15)


def score_quality(job) -> int:
    score = 0

    if job.salary_min and job.salary_max:
        score += 10

    if job.url:
        score += 5

    if job.source == "greenhouse":
        score += 10
    elif job.source == "himalayas":
        score += 8
    else:
        score += 5

    if job.is_remote:
        score += 5

    return min(score, 30)


def calculate_ranking_score(job) -> float:
    with get_session() as session:
        raw = session.query(RawJobDB).filter(
            RawJobDB.job_hash == job.job_hash
        ).first()
        description = raw.description if raw else ""

    skills = score_skills(description, job.title or "")
    experience = score_experience(job.experience_level or "mid")
    quality = score_quality(job)

    total = skills + experience + quality
    return round(total, 2)


def score_all_jobs() -> dict:
    scored = 0
    errors = 0

    with get_session() as session:
        jobs = session.query(JobDB).filter(
            JobDB.ranking_score == 0.0
        ).all()

        logger.info(f"Scoring {len(jobs)} jobs")

        for job in jobs:
            try:
                score = calculate_ranking_score(job)
                job.ranking_score = score
                scored += 1
            except Exception as e:
                logger.error(f"Error scoring job {job.title}: {e}")
                errors += 1
                continue

    logger.info(f"Scored {scored} jobs, {errors} errors")
    return {"scored": scored, "errors": errors}