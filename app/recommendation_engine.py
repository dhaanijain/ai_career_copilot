

"""
app/recommendation_engine.py — AI Career Copilot
Full AI-powered job recommendation engine.

Pipeline:
  1  Resume   — OCR + FAISS RAG pipeline extracts canonical skill list
  2  Fetch    — Adzuna API returns a pool of live job listings
  3  Score    — JD skills extracted per job; scored against resume semantically
  4  Rank     — Jobs sorted by weighted similarity score + exact match count
  5  Output   — Top-N results printed to terminal and saved as JSON

Public API
----------
recommend_jobs(resume_path, query, location, top_n) → List[dict]
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .job_fetcher import fetch_jobs
from .rag_pipeline import run_pipeline
from .scoring_engine import MatchResult, score_match
from .skill_extractor import extract_skills_from_text

logger = logging.getLogger(__name__)

# Fetch this many × top_n jobs so the ranker has a meaningful pool to work with.
_FETCH_MULTIPLIER = 4
_MIN_FETCH = 20

# Descriptions shorter than this are considered malformed and skipped.
_MIN_DESCRIPTION_CHARS = 30

_OUTPUTS_DIR = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs")
)


# ---------------------------------------------------------------------------
# Data class
# ---------------------------------------------------------------------------

@dataclass
class JobRecommendation:
    """All data needed to present one ranked job recommendation."""

    title: str
    company: str
    location: str
    match_score: int                        # 0–100 integer percentage
    matching_skills: List[str]              # exact resume ↔ JD matches
    semantic_matches: List[Dict[str, Any]]  # {"resume_skill", "jd_skill", "similarity"}
    missing_skills: List[str]               # JD skills with no resume coverage
    recommendations: List[str]             # actionable improvement tips
    redirect_url: str

    def to_dict(self) -> Dict[str, Any]:
        """JSON-serialisable dict — ready for REST APIs, Streamlit state, or file output."""
        return {
            "title": self.title,
            "company": self.company,
            "location": self.location,
            "match_score": self.match_score,
            "matching_skills": self.matching_skills,
            "semantic_matches": self.semantic_matches,
            "missing_skills": self.missing_skills,
            "recommendations": self.recommendations,
            "redirect_url": self.redirect_url,
        }


# ---------------------------------------------------------------------------
# Step 3 — per-job scoring
# ---------------------------------------------------------------------------

def _score_job(
    resume_skills: List[str],
    job: Dict[str, Any],
) -> Optional[JobRecommendation]:
    """
    Extract JD skills from one job description and score it against the resume.

    Returns None when:
    - description is too short / malformed to be useful
    - skill extraction or scoring raises an unexpected exception
    """
    description: str = job.get("description", "") or ""

    if len(description.strip()) < _MIN_DESCRIPTION_CHARS:
        logger.debug(
            "Skipping %r — description too short (%d chars)",
            job.get("title"), len(description),
        )
        return None

    try:
        jd_skills = extract_skills_from_text(description)
    except Exception as exc:
        logger.warning("Skill extraction failed for %r: %s", job.get("title"), exc)
        jd_skills = []

    try:
        result: MatchResult = score_match(resume_skills, jd_skills)
    except Exception as exc:
        logger.warning("Scoring failed for %r: %s", job.get("title"), exc)
        return None

    return JobRecommendation(
        title=job.get("title", "N/A"),
        company=job.get("company", "N/A"),
        location=job.get("location", "N/A"),
        match_score=round(result.match_score * 100),
        matching_skills=result.exact_matches,
        semantic_matches=[
            {
                "resume_skill": m.resume_skill,
                "jd_skill": m.jd_skill,
                "similarity": m.similarity,
            }
            for m in result.semantic_matches
        ],
        missing_skills=result.missing_skills,
        recommendations=result.recommendations,
        redirect_url=job.get("redirect_url", "N/A"),
    )


# ---------------------------------------------------------------------------
# Step 4 — ranking
# ---------------------------------------------------------------------------

def _rank_jobs(recs: List[JobRecommendation]) -> List[JobRecommendation]:
    """
    Three-key sort:
      1. match_score descending       — primary quality signal
      2. len(matching_skills) desc    — more exact matches wins tiebreaks
      3. len(missing_skills) asc      — fewer gaps is better among equals
    """
    return sorted(
        recs,
        key=lambda r: (-r.match_score, -len(r.matching_skills), len(r.missing_skills)),
    )


# ---------------------------------------------------------------------------
# Step 5 — output
# ---------------------------------------------------------------------------

def _save_results(recs: List[JobRecommendation], path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([r.to_dict() for r in recs], f, indent=2, ensure_ascii=False)


def _print_results(
    resume_skills: List[str],
    jobs_fetched: int,
    recs: List[JobRecommendation],
    output_path: str,
) -> None:
    W = 62
    bar = "═" * W

    print(f"\n{bar}")
    print("  AI Career Copilot — Job Recommendations")
    print(bar)
    print(f"  📄 Resume Skills Extracted : {len(resume_skills)}")
    print(f"  🌐 Jobs Fetched            : {jobs_fetched}")
    print(f"  🏆 Top Matches Found       : {len(recs)}")
    print(f"{bar}\n")

    if not recs:
        print("  ⚠  No recommendations generated.")
        print("     Try a broader query or check your API credentials.\n")
        return

    print("  🏆 Ranked Recommendations:\n")
    for i, rec in enumerate(recs, 1):
        print(f"  {i}. {rec.title} — {rec.match_score}%")

    for i, rec in enumerate(recs, 1):
        print(f"\n  {'─' * (W - 2)}")
        print(f"  [{i}] {rec.title}")
        print(f"       Company  : {rec.company}")
        print(f"       Location : {rec.location}")
        print(f"       Match    : {rec.match_score}%")
        print(f"       URL      : {rec.redirect_url}")

        if rec.matching_skills:
            print(f"\n       ✅ Matching Skills ({len(rec.matching_skills)}):")
            for s in rec.matching_skills:
                print(f"          • {s}")

        if rec.semantic_matches:
            print(f"\n       🔗 Semantic Matches ({len(rec.semantic_matches)}):")
            for m in rec.semantic_matches:
                print(f"          • {m['resume_skill']} ↔ {m['jd_skill']} ({m['similarity']:.0%})")

        if rec.missing_skills:
            print(f"\n       ❌ Missing Skills ({len(rec.missing_skills)}):")
            for s in rec.missing_skills:
                print(f"          • {s}")

        if rec.recommendations:
            print(f"\n       💡 Recommendations:")
            for tip in rec.recommendations[:3]:
                print(f"          → {tip}")

    print(f"\n{bar}")
    print(f"  Results saved → {output_path}")
    print(f"{bar}\n")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def recommend_jobs(
    resume_path: str,
    query: str = "Machine Learning Engineer",
    location: str = "India",
    top_n: int = 5,
) -> List[Dict[str, Any]]:
    """
    Full AI-powered job recommendation pipeline.

    Args:
        resume_path: Path to a PDF resume (absolute or relative to CWD).
        query:       Adzuna search query — job title or role keywords.
        location:    Geographic filter passed to Adzuna (e.g. "India", "Bangalore").
        top_n:       Number of top recommendations to return and save.

    Returns:
        List of recommendation dicts — each with:
          title, company, location, match_score (0-100),
          matching_skills, semantic_matches, missing_skills,
          recommendations, redirect_url.

    Raises:
        FileNotFoundError: when resume_path does not point to a real file.
    """
    if not os.path.isfile(resume_path):
        raise FileNotFoundError(f"Resume not found: {resume_path!r}")

    # ── Step 1: Resume skill extraction ──────────────────────────────────────
    resume_skills = run_pipeline(resume_path)
    if not resume_skills:
        logger.warning("No skills extracted from resume — recommendation quality will be low.")

    # ── Step 2: Fetch live jobs from Adzuna ───────────────────────────────────
    fetch_count = max(_MIN_FETCH, top_n * _FETCH_MULTIPLIER)
    jobs = fetch_jobs(query=query, location=location, results=fetch_count)

    if not jobs:
        print(
            "\n  ⚠  No jobs returned from Adzuna.\n"
            "     Check your credentials or try a different query.\n"
        )
        return []

    # ── Step 3: Score each job against resume skills ──────────────────────────
    print(f"\n  🔍 Scoring {len(jobs)} job(s) against your resume skills…")

    scored: List[JobRecommendation] = []
    for job in jobs:
        rec = _score_job(resume_skills, job)
        if rec is not None:
            scored.append(rec)

    if not scored:
        print("\n  ⚠  All job descriptions were too short or malformed to score.\n")
        return []

    # ── Step 4: Rank and trim to top_n ───────────────────────────────────────
    ranked = _rank_jobs(scored)[:top_n]

    # ── Step 5: Save and print ────────────────────────────────────────────────
    output_path = os.path.join(_OUTPUTS_DIR, "job_recommendations.json")
    _save_results(ranked, output_path)
    _print_results(resume_skills, len(jobs), ranked, output_path)

    return [r.to_dict() for r in ranked]
