import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    postgres_host = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port = int(os.getenv("POSTGRES_PORT", 5432))
    postgres_user = os.getenv("POSTGRES_USER", "dejobs")
    postgres_password = os.getenv("POSTGRES_PASSWORD", "dejobs_pass")
    postgres_db = os.getenv("POSTGRES_DB", "de_jobs")

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+psycopg2://{self.postgres_user}:"
            f"{self.postgres_password}@{self.postgres_host}:"
            f"{self.postgres_port}/{self.postgres_db}"
        )

    gmail_user = os.getenv("GMAIL_USER", "")
    gmail_app_pass = os.getenv("GMAIL_APP_PASS", "")
    alert_email = os.getenv("ALERT_EMAIL", "")
    alert_email_2 = os.getenv("ALERT_EMAIL_2", "")

    pipeline_schedule = "0 6 * * *"
    min_trust_score = 40
    request_timeout = 30
    request_delay = 0.5
    max_retries = 3

    target_roles = [
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

    priority_skills = [
        "python", "sql", "airflow", "spark", "kafka",
        "dbt", "snowflake", "databricks", "aws", "gcp",
        "azure", "docker", "kubernetes", "terraform",
        "redshift", "bigquery", "postgres", "etl", "elt",
    ]


settings = Settings()