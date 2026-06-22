-- Runs once when the Postgres container first starts.
-- Creates the Airflow database alongside our main de_jobs database.

SELECT 'CREATE DATABASE airflow'
WHERE NOT EXISTS (
    SELECT FROM pg_database WHERE datname = 'airflow'
)\gexec

-- Create a dedicated Airflow user
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'airflow') THEN
        CREATE ROLE airflow WITH LOGIN PASSWORD 'airflow';
    END IF;
END
$$;

GRANT ALL PRIVILEGES ON DATABASE airflow TO airflow;
