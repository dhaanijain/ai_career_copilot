"""
test_api.py — AI Career Copilot
Quick smoke-test for the Adzuna job fetcher.

Usage (from the project root with the venv active):
    python test_api.py

Requires ADZUNA_APP_ID and ADZUNA_APP_KEY to be set in .env.
"""

import logging
import sys

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")

from app.job_fetcher import fetch_jobs


def main() -> None:
    query = "Machine Learning Engineer"
    location = "India"
    results = 5

    print(f"\n{'═' * 60}")
    print(f"  Adzuna Job Fetcher — Live API Test")
    print(f"{'═' * 60}")
    print(f"  Query    : {query}")
    print(f"  Location : {location}")
    print(f"  Limit    : {results} results\n")

    jobs = fetch_jobs(query=query, location=location, results=results)

    if not jobs:
        print("  No jobs returned. Check your .env credentials or query.")
        sys.exit(1)

    print(f"  {len(jobs)} job(s) fetched:\n")
    print(f"  {'─' * 56}")

    for i, job in enumerate(jobs, 1):
        print(f"  [{i}] {job['title']}")
        print(f"      Company  : {job['company']}")
        print(f"      Location : {job['location']}")
        print(f"      URL      : {job['redirect_url']}")
        print()

    print(f"{'═' * 60}\n")


if __name__ == "__main__":
    main()
