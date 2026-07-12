import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# load env variables directly
from dotenv import load_dotenv
load_dotenv("/opt/airflow/dags/.env")

default_args = {
    "owner": "abdullahi",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
    "start_date": datetime(2026, 7, 1),
}

dag = DAG(
    dag_id="jobs_pipeline",
    default_args=default_args,
    description="daily job scraping and alert pipeline",
    schedule_interval="0 6 * * *",
    catchup=False,
    tags=["jobs", "pipeline"],
)


def run_scrapers():
    sys.path.insert(0, "/opt/airflow/dags")
    from scrapers.scraper_greenhouse import GreenhouseScraper
    from scrapers.scraper_himalayas import HimalayasScraper
    from scrapers.scraper_wfhng import WFHNGScraper
    from pipeline.loader import load_raw_jobs

    all_jobs = []
    all_jobs += GreenhouseScraper().scrape()
    all_jobs += HimalayasScraper().scrape()
    all_jobs += WFHNGScraper().scrape()

    result = load_raw_jobs(all_jobs)
    print(f"Inserted: {result['inserted']}, Updated: {result['updated']}, Skipped: {result['skipped']}")


def run_cleaner():
    sys.path.insert(0, "/opt/airflow/dags")
    from pipeline.cleaner import clean_jobs
    result = clean_jobs()
    print(f"Accepted: {result['accepted']}, Rejected: {result['rejected']}")


def run_scorer():
    sys.path.insert(0, "/opt/airflow/dags")
    from pipeline.trust_scorer import score_all_jobs
    result = score_all_jobs()
    print(f"Scored: {result['scored']}")


def run_email():
    sys.path.insert(0, "/opt/airflow/dags")
    from pipeline.email_alert import send_daily_alerts
    send_daily_alerts()
    print("Email alerts sent")


scrape_task = PythonOperator(
    task_id="scrape_and_load",
    python_callable=run_scrapers,
    dag=dag,
)

clean_task = PythonOperator(
    task_id="clean_jobs",
    python_callable=run_cleaner,
    dag=dag,
)

score_task = PythonOperator(
    task_id="score_jobs",
    python_callable=run_scorer,
    dag=dag,
)

email_task = PythonOperator(
    task_id="send_email",
    python_callable=run_email,
    dag=dag,
)

scrape_task >> clean_task >> score_task >> email_task