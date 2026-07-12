import json
import requests
import concurrent.futures
import time

# load the raw company list we copied from the aggregator project
with open("data/companies/raw_greenhouse_companies.json") as f:
    all_companies = json.load(f)

# remove obvious junk - pure numbers or oddly short/long names
clean_companies = [
    c for c in all_companies
    if not c.isdigit() and 2 <= len(c) <= 40
]

print(f"Total companies to check: {len(clean_companies)}")

verified = []
checked = 0


def check_company(slug):
    url = f"https://boards-api.greenhouse.io/v1/boards/{slug}/jobs"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            jobs = response.json().get("jobs", [])
            if len(jobs) > 0:
                return slug
    except requests.RequestException:
        pass
    return None


# check 30 companies at the same time instead of one by one
with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
    futures = {executor.submit(check_company, slug): slug for slug in clean_companies}

    for future in concurrent.futures.as_completed(futures):
        checked += 1
        result = future.result()
        if result:
            verified.append(result)

        if checked % 200 == 0:
            print(f"Checked {checked}/{len(clean_companies)} - {len(verified)} verified so far")

print(f"\nDone. {len(verified)} companies verified out of {len(clean_companies)}")

with open("data/companies/verified_greenhouse_companies.json", "w") as f:
    json.dump(verified, f, indent=2)

print("Saved to data/companies/verified_greenhouse_companies.json")