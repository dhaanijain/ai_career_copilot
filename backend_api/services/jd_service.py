"""
backend_api/services/jd_service.py — AI Career Copilot
JD matching service with optional Supabase persistence.
"""

from pathlib import Path
from typing import Optional

from app.jd_matcher import match_resume_to_jd


def match(resume_path: Path, jd_text: str) -> dict:
    result = match_resume_to_jd(str(resume_path), jd_text)
    return {
        "match_score": round(result.match_score * 100, 1),
        "confidence": result.confidence,
        "total_jd_skills": len(result.jd_skills),
        "matching_skills": result.exact_matches,
        "semantic_matches": [
            {
                "resume_skill": m.resume_skill,
                "jd_skill": m.jd_skill,
                "similarity": m.similarity,
            }
            for m in result.semantic_matches
        ],
        "missing_skills": result.missing_skills,
        "recommendations": result.recommendations,
        "category_tips": {},
        # Internal fields used for DB persistence
        "_jd_skills": result.jd_skills,
        "_exact_matches": result.exact_matches,
        "_partially_matched": result.partially_matched,
        "_match_score_raw": result.match_score,
        "_match_score_pct": f"{result.match_score * 100:.1f}%",
        "_resume_skill_count": len(result.resume_skills),
        "_jd_skill_count": len(result.jd_skills),
        "_semantic_matches_raw": [
            {
                "resume_skill": m.resume_skill,
                "jd_skill": m.jd_skill,
                "similarity": m.similarity,
            }
            for m in result.semantic_matches
        ],
    }


def save_jd_match_to_supabase(
    match_result: dict,
    resume_id: str,
    user_id: str,
    jd_text: str,
    jd_title: Optional[str] = None,
) -> Optional[str]:
    """
    Persist a JD match result to public.jd_matches.
    Returns the new row id, or None if the save failed.
    """
    try:
        from app.config.supabase import get_supabase_client
        client = get_supabase_client()

        row = {
            "user_id": user_id,
            "resume_id": resume_id,
            "jd_title": jd_title,
            "jd_text": jd_text,
            "match_score": match_result["_match_score_raw"],
            "match_score_pct": match_result["_match_score_pct"],
            "confidence": match_result["confidence"],
            "resume_skill_count": match_result["_resume_skill_count"],
            "jd_skill_count": match_result["_jd_skill_count"],
            "jd_skills": match_result["_jd_skills"],
            "exact_matches": match_result["_exact_matches"],
            "semantic_matches": match_result["_semantic_matches_raw"],
            "missing_skills": match_result["missing_skills"],
            "partially_matched": match_result["_partially_matched"],
            "recommendations": match_result["recommendations"],
        }

        response = client.table("jd_matches").insert(row).execute()
        return response.data[0]["id"] if response.data else None

    except Exception as exc:
        print(f"[jd_service] Supabase save failed (non-fatal): {exc}")
        return None
