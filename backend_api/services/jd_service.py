from pathlib import Path
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
    }
