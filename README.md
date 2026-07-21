# DE Jobs Intelligence Pipeline

A portfolio project, but also something I actually use. Most "worldwide remote" job listings aren't. Half of them bury a US-only requirement somewhere in the description, and the rest are onsite roles mislabeled as remote. This pipeline scrapes, filters, and scores remote data engineering and product management jobs every day, and only shows me the ones actually worth applying to.

## What it does

Every day at 6am, the pipeline scrapes fresh listings, filters out onsite and location-restricted roles, scores each job against my skills, refreshes the dbt models, and emails a digest of the day's best matches. A separate weekly job re-checks over 8,300 companies and keeps the list of active employers current, so I'm not maintaining it by hand.

## Data Sources

- **Greenhouse** — 1,287 verified companies, pulled from a public index and re-verified weekly
- **Himalayas** — remote job board, scanned for relevant titles
- **WorkFromHome.ng** — jobs curated for African remote workers

## Tools Used

| Layer | Tool |
|---|---|
| Ingestion | Python (requests, BeautifulSoup) |
| Orchestration | Apache Airflow running in Docker |
| Storage | PostgreSQL |
| Transformation | dbt |
| Visualization | Streamlit |
| Testing | pytest (31 tests) |

## How the pipeline runs

The daily DAG runs these steps in order:

1. Scrape Greenhouse, Himalayas, and WorkFromHome.ng
2. Load into PostgreSQL, deduplicating against everything already scraped
3. Clean — drop onsite/hybrid roles, parse salaries, flag jobs whose descriptions mention visa sponsorship or in-office requirements
4. Score each job 0-100, with a different skill rubric for data engineering versus product management roles
5. Refresh the dbt models
6. Email the day's new matches, sorted by score

A second DAG runs weekly, re-verifying which companies are still active on Greenhouse and updating the list the daily scraper reads from.

## dbt Models

- `stg_jobs` — cleaned, standardized view of active jobs
- `fct_active_jobs` — jobs scoring 45 or above, ready to browse

## Dashboard

The Streamlit dashboard shows filterable job cards by role type, score, experience level, and location restriction. Jobs get flagged if their description hints at visa or on-site requirements, even when the listing itself says "remote." Skills in demand and top hiring companies update live based on whichever role type is selected.

## Why it's built this way

Two separate DAGs, because the daily scrape and the weekly company refresh run on different schedules for different reasons. One failing shouldn't take the other down with it.

One config file for scoring, `role_skills.py`, shared by both the scorer and the dashboard. Data engineering and product management jobs need different criteria, and I didn't want two skill lists quietly drifting out of sync in two different files.

Deduplication by content hash. Job boards don't give you a stable ID to track a posting over time, so every job gets hashed from its title, company, and URL. Scrape the same job twice and it updates the existing row instead of duplicating it.

## Status

Scraping, cleaning, scoring, dbt, and email alerts run daily on their own. The dashboard runs locally for now. A hosted version is next, once I've settled on where to run it for free.
