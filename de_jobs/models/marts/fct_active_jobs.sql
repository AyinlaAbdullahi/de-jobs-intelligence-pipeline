select
    job_hash,
    title,
    company_name,
    location,
    experience_level,
    source,
    url,
    salary_min,
    salary_max,
    salary_currency,
    ranking_score,
    beginner_friendly,
    is_remote,
    posted_at,
    created_at
from {{ ref('stg_jobs') }}
where ranking_score >= 45
order by ranking_score desc
