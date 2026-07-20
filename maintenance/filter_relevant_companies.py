import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import requests
import concurrent.futures
from app_config.settings import settings

with open("data/companies/verified_greenhouse_companies.json") as f:
    verified_companies = json.load(f)

print(f"Checking {len(verified_companies)} companies for relevant roles")

relevant_companies = []
checked = 0


def is_relevant_title(title):
    title_lower = title.lower()
    return any(role in title_lower for role in settings.target_roles)


def check_company_relevance(slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            matching_jobs = [j for j in jobs if is_relevant_title(j.get("title", ""))]
            if matching_jobs:
                return {
                    "slug": slug,
                    "total_jobs": len(jobs),
                    "matching_jobs": len(matching_jobs),
                }
    except requests.RequestException:
        pass
    return None


with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    futures = {
        executor.submit(check_company_relevance, slug): slug
        for slug in verified_companies
    }

    for future in concurrent.futures.as_completed(futures):
        checked += 1
        result = future.result()
        if result:
            relevant_companies.append(result)

        if checked % 200 == 0:
            print(f"Checked {checked}/{len(verified_companies)} - {len(relevant_companies)} relevant so far")

print(f"\nDone. {len(relevant_companies)} companies have relevant roles out of {len(verified_companies)}")

relevant_companies.sort(key=lambda c: c["matching_jobs"], reverse=True)

with open("data/companies/relevant_greenhouse_companies.json", "w") as f:
    json.dump(relevant_companies, f, indent=2)

print("Saved to data/companies/relevant_greenhouse_companies.json")