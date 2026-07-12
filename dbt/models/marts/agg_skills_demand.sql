select
    skill,
    count(*) as job_count
from {{ ref('stg_jobs') }},
unnest(string_to_array(lower(title), ' ')) as skill
where skill in (
    'python', 'sql', 'airflow', 'dbt', 'spark', 'kafka',
    'docker', 'kubernetes', 'snowflake', 'databricks',
    'azure', 'aws', 'gcp', 'postgres', 'etl', 'pipeline'
)
group by skill
order by job_count desc
