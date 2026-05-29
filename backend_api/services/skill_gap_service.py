from pathlib import Path
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
    }
