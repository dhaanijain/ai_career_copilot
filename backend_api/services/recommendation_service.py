from pathlib import Path
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
