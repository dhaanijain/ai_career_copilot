"""
app/job_fetcher.py — AI Career Copilot
Fetches live job listings from the Adzuna Jobs API.

Public API
----------
fetch_jobs(query, location, results) → List[dict]

Each returned dict has keys: title, company, location, description, redirect_url.
"""

import logging
from typing import Any, Dict, List

import requests

from .config import APP_ID, APP_KEY

logger = logging.getLogger(__name__)

_ADZUNA_ENDPOINT = "https://api.adzuna.com/v1/api/jobs/in/search/1"
_REQUEST_TIMEOUT = 10  # seconds


def fetch_jobs(
    query: str,
    location: str = "India",
    results: int = 10,
) -> List[Dict[str, Any]]:
    """
    Fetch live job listings from the Adzuna Jobs API.

    Args:
        query:    Search query — typically a job title or skill set
                  (e.g. "Machine Learning Engineer", "Python Developer").
        location: Geographic filter passed to Adzuna (default: "India").
        results:  Maximum number of listings to return (default: 10).

    Returns:
        List of job dicts, each containing:
            title, company, location, description, redirect_url.
        Returns an empty list on any non-fatal error so callers can
        degrade gracefully.

    Raises:
        Nothing — all errors are logged and an empty list is returned,
        keeping the calling pipeline resilient to transient API failures.
    """
    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": results,
        "what": query,
        "where": location,
        "content-type": "application/json",
    }

    logger.info("Fetching jobs from Adzuna: query=%r, location=%r, results=%d", query, location, results)

    try:
        response = requests.get(_ADZUNA_ENDPOINT, params=params, timeout=_REQUEST_TIMEOUT)
        response.raise_for_status()
    except requests.exceptions.Timeout:
        logger.error("Adzuna API request timed out after %ds.", _REQUEST_TIMEOUT)
        return []
    except requests.exceptions.ConnectionError as exc:
        logger.error("Network error connecting to Adzuna API: %s", exc)
        return []
    except requests.exceptions.HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else "unknown"
        logger.error("Adzuna API returned HTTP %s: %s", status, exc)
        return []
    except requests.exceptions.RequestException as exc:
        logger.error("Unexpected error during Adzuna API request: %s", exc)
        return []

    try:
        data = response.json()
    except ValueError:
        logger.error("Adzuna API returned invalid JSON. Raw response: %s", response.text[:200])
        return []

    raw_jobs: List[Dict] = data.get("results", [])

    if not raw_jobs:
        logger.warning("Adzuna returned 0 results for query=%r, location=%r.", query, location)
        return []

    logger.info("Adzuna returned %d job(s).", len(raw_jobs))
    return [_parse_job(job) for job in raw_jobs]


def _parse_job(raw: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise a single raw Adzuna result into a consistent schema."""
    return {
        "title": raw.get("title", "N/A"),
        "company": raw.get("company", {}).get("display_name", "N/A"),
        "location": raw.get("location", {}).get("display_name", "N/A"),
        "description": raw.get("description", "N/A"),
        "redirect_url": raw.get("redirect_url", "N/A"),
    }
