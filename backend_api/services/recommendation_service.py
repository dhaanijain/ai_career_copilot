"""
backend_api/services/recommendation_service.py — AI Career Copilot
Job recommendation service with optional Supabase persistence.
"""

from pathlib import Path
from typing import Optional

from app.recommendation_engine import recommend_jobs
from app.rag_pipeline import run_pipeline


def get_recommendations(
    resume_path: Path,
    query: str = "machine learning engineer",
    location: str = "",
    top_n: int = 10,
) -> dict:
    resume_skills = run_pipeline(str(resume_path))
    jobs_raw = recommend_jobs(str(resume_path), query=query, location=location, top_n=top_n)

    jobs = []
    for job in jobs_raw:
        semantic = []
        for sm in job.get("semantic_matches", []):
            if isinstance(sm, dict):
                semantic.append({
                    "resume_skill": sm.get("resume_skill", ""),
                    "jd_skill": sm.get("jd_skill", ""),
                    "similarity": float(sm.get("similarity", 0)),
                })
        jobs.append({
            "title": job.get("title", ""),
            "company": job.get("company", ""),
            "location": job.get("location", ""),
            "match_score": float(job.get("match_score", 0)),
            "matching_skills": job.get("matching_skills", []),
            "semantic_matches": semantic,
            "missing_skills": job.get("missing_skills", []),
            "recommendations": job.get("recommendations", []),
            "redirect_url": job.get("redirect_url", ""),
        })

    return {
        "jobs": jobs,
        "total_jobs": len(jobs),
        "resume_skills": resume_skills,
    }


def save_recommendations_to_supabase(
    result: dict,
    resume_id: str,
    user_id: str,
    query: str,
    location: str,
    top_n: int,
    total_fetched: int = 0,
) -> Optional[str]:
    """
    Persist a recommendation session and all ranked jobs to Supabase.
    Returns the session id, or None if the save failed.
    """
    try:
        from app.config.supabase import get_supabase_client
        client = get_supabase_client()

        # 1. Insert the session row
        session_row = {
            "user_id": user_id,
            "resume_id": resume_id,
            "search_query": query,
            "location_filter": location,
            "top_n": top_n,
            "resume_skills": result["resume_skills"],
            "total_fetched": total_fetched,
            "total_ranked": result["total_jobs"],
        }
        session_resp = client.table("job_recommendation_sessions").insert(session_row).execute()
        if not session_resp.data:
            return None
        session_id = session_resp.data[0]["id"]

        # 2. Insert individual job rows
        job_rows = [
            {
                "session_id": session_id,
                "user_id": user_id,
                "title": job["title"],
                "company": job["company"],
                "location": job["location"],
                "redirect_url": job["redirect_url"],
                "match_score": int(job["match_score"]),
                "matching_skills": job["matching_skills"],
                "semantic_matches": job["semantic_matches"],
                "missing_skills": job["missing_skills"],
                "recommendations": job["recommendations"],
                "rank": idx + 1,
            }
            for idx, job in enumerate(result["jobs"])
        ]
        if job_rows:
            client.table("job_recommendations").insert(job_rows).execute()

        return session_id

    except Exception as exc:
        print(f"[recommendation_service] Supabase save failed (non-fatal): {exc}")
        return None
