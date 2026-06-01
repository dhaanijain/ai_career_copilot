"""
backend_api/services/skill_gap_service.py — AI Career Copilot
Skill gap analysis service with optional Supabase persistence.
"""

from pathlib import Path
from typing import Optional

from app.rag_pipeline import run_pipeline
from app.jd_matcher import match_resume_to_jd

MODERN_TECH_REFERENCE = """
Python Machine Learning Deep Learning PyTorch TensorFlow Scikit-learn
Pandas NumPy SQL NoSQL PostgreSQL MongoDB Redis Elasticsearch
AWS Azure Google Cloud Docker Kubernetes CI/CD GitHub Actions Terraform
FastAPI Django REST API GraphQL Microservices Node.js
Natural Language Processing Computer Vision MLflow
Hugging Face Transformers LangChain RAG Vector Database
Apache Spark Apache Kafka Distributed Systems
React TypeScript Next.js System Design Linux Git
"""


def analyze(resume_path: Path, jd_text: str | None = None) -> dict:
    reference = jd_text if jd_text and jd_text.strip() else MODERN_TECH_REFERENCE
    reference_used = "custom" if jd_text and jd_text.strip() else "built_in"
    resume_skills = run_pipeline(str(resume_path))
    result = match_resume_to_jd(str(resume_path), reference)

    return {
        "resume_skills": resume_skills,
        "missing_skills": result.missing_skills,
        "semantic_gaps": [
            {
                "resume_skill": m.resume_skill,
                "jd_skill": m.jd_skill,
                "similarity": m.similarity,
            }
            for m in result.semantic_matches
        ],
        "recommendations": result.recommendations,
        "category_tips": {},
        "match_score": round(result.match_score * 100, 1),
        # Internal field used for DB persistence
        "_reference_used": reference_used,
    }


def save_skill_gap_to_supabase(
    analysis: dict,
    resume_id: str,
    user_id: str,
    jd_text: Optional[str],
) -> Optional[str]:
    """
    Persist a skill gap analysis result to public.skill_gap_analyses.
    Returns the new row id, or None if the save failed.
    """
    try:
        from app.config.supabase import get_supabase_client
        client = get_supabase_client()

        row = {
            "user_id": user_id,
            "resume_id": resume_id,
            "jd_text": jd_text if jd_text and jd_text.strip() else None,
            "reference_used": analysis.get("_reference_used", "built_in"),
            "match_score": analysis["match_score"],
            "resume_skills": analysis["resume_skills"],
            "missing_skills": analysis["missing_skills"],
            "semantic_gaps": analysis["semantic_gaps"],
            "recommendations": analysis["recommendations"],
            "category_tips": analysis["category_tips"],
        }

        response = client.table("skill_gap_analyses").insert(row).execute()
        return response.data[0]["id"] if response.data else None

    except Exception as exc:
        print(f"[skill_gap_service] Supabase save failed (non-fatal): {exc}")
        return None
