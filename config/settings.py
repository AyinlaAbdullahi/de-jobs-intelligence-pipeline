from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):

    # Database
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "dejobs"
    postgres_password: str = "dejobs_pass"
    postgres_db: str = "de_jobs"

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    # Email alerts
    gmail_user: str = ""
    gmail_app_pass: str = ""
    alert_email: str = ""

    # Pipeline
    pipeline_schedule: str = "0 6 * * *"
    min_trust_score: int = 40
    request_timeout: int = 30
    request_delay: float = 0.5
    max_retries: int = 3

    # Filters
    target_roles: list[str] = [
    "data engineer",
    "analytics engineer",
    "etl developer",
    "etl engineer",
    "data platform engineer",
    "data warehouse engineer",
    "big data engineer",
    "cloud data engineer",
    "analytics data engineer",
    "staff data engineer",
    "senior data engineer",
    "junior data engineer",
    "product manager",
    "technical product manager",
    "senior product manager",
    "associate product manager",
    "junior product manager",
    "product management",
]

    priority_skills: list[str] = [
        "python", "sql", "airflow", "spark", "kafka",
        "dbt", "snowflake", "databricks", "aws", "gcp",
        "azure", "docker", "kubernetes", "terraform",
        "redshift", "bigquery", "postgres", "etl", "elt",
    ]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()