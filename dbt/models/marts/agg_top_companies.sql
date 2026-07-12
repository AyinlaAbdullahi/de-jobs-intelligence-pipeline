select
    company_name,
    count(*) as job_count,
    round(avg(ranking_score)::numeric, 1) as avg_score,
    max(ranking_score) as top_score
from {{ ref('stg_jobs') }}
group by company_name
order by job_count desc
limit 20
