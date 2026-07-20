import sys
import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

from dotenv import load_dotenv
load_dotenv("/opt/airflow/dags/.env")
os.environ["POSTGRES_HOST"] = "host.docker.internal"

default_args = {
    "owner": "abdullahi",
    "retries": 1,
    "retry_delay": timedelta(minutes=10),
    "start_date": datetime(2026, 7, 1),
}

dag = DAG(
    dag_id="refresh_companies",
    default_args=default_args,
    description="weekly refresh of verified greenhouse companies list",
    schedule_interval="0 3 * * 0",
    catchup=False,
    tags=["maintenance", "companies"],
)


def run_verification():
    sys.path.insert(0, "/opt/airflow/dags")
    os.chdir("/opt/airflow/dags")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "verify_greenhouse_companies",
        "/opt/airflow/dags/maintenance/verify_greenhouse_companies.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def run_relevance_filter():
    sys.path.insert(0, "/opt/airflow/dags")
    os.chdir("/opt/airflow/dags")
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "filter_relevant_companies",
        "/opt/airflow/dags/maintenance/filter_relevant_companies.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


verify_task = PythonOperator(
    task_id="verify_companies",
    python_callable=run_verification,
    dag=dag,
)

filter_task = PythonOperator(
    task_id="filter_relevant_companies",
    python_callable=run_relevance_filter,
    dag=dag,
)

verify_task >> filter_task