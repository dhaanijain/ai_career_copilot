"""
test_recommendations.py — AI Career Copilot
Runs the full job recommendation engine and prints ranked results.

Usage
-----
Default (uses built-in resume + query):
    python test_recommendations.py

Custom resume / query / location / top-N:
    python test_recommendations.py <resume.pdf> <query> <location> <top_n>

Examples:
    python test_recommendations.py
    python test_recommendations.py data/Dhaani_Jain_resume.pdf "Data Scientist" "Bangalore" 3
    python test_recommendations.py data/Dhaani_Jain_resume.pdf "NLP Engineer" "India" 5
"""

import os
import sys


def main() -> None:
    resume_path = sys.argv[1] if len(sys.argv) > 1 else os.path.join("data", "Dhaani_Jain_resume.pdf")
    query       = sys.argv[2] if len(sys.argv) > 2 else "Machine Learning Engineer"
    location    = sys.argv[3] if len(sys.argv) > 3 else "India"
    top_n       = int(sys.argv[4]) if len(sys.argv) > 4 else 5

    from app.recommendation_engine import recommend_jobs

    recommendations = recommend_jobs(
        resume_path=resume_path,
        query=query,
        location=location,
        top_n=top_n,
    )

    if not recommendations:
        print("No recommendations generated.")
        return

    print(f"\n  📊 Summary — Top {len(recommendations)} Recommended Jobs:\n")
    for i, job in enumerate(recommendations, 1):
        score = job["match_score"]
        exact = len(job["matching_skills"])
        missing = len(job["missing_skills"])
        print(
            f"  {i:>2}. [{score:>3}%] {job['title']:<40} "
            f"✅ {exact} matched  ❌ {missing} missing"
        )

    print()


if __name__ == "__main__":
    main()
