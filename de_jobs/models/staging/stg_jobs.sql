select
    id,
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
from public.jobs
where is_active = true
