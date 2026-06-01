"""
app/scoring_engine.py — AI Career Copilot
Resume ↔ JD scoring engine: exact matching, semantic matching, gap analysis,
and rule-based recommendation generation.

Public API
----------
score_match(resume_skills, jd_skills) → MatchResult
MatchResult.to_dict()                 → JSON-serialisable dict
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Set, Tuple

from .embedding_engine import build_skill_index, get_skill_embeddings
from .utils import normalize_skill_name

# ---------------------------------------------------------------------------
# Tunable constants — adjust here without touching matching logic below
# ---------------------------------------------------------------------------

SEMANTIC_MATCH_THRESHOLD: float = 0.80
SEMANTIC_MATCH_WEIGHT: float = 0.65
_HIGH_CONFIDENCE_MIN_JD_SKILLS: int = 8
_MEDIUM_CONFIDENCE_MIN_JD_SKILLS: int = 4

# ---------------------------------------------------------------------------
# Per-skill actionable tips
# ---------------------------------------------------------------------------

_SKILL_TIPS: Dict[str, str] = {
    "Docker": "learn images, containers, Dockerfile, and docker-compose",
    "Kubernetes": "study pods, deployments, services, and the kubectl CLI",
    "AWS": "complete AWS Cloud Practitioner; explore EC2, S3, and Lambda",
    "Azure": "start with the AZ-900 Azure Fundamentals certification path",
    "GCP": "explore Google Cloud Digital Leader or Associate Cloud Engineer",
    "Terraform": "practice IaC with Terraform on a free-tier cloud account",
    "CI/CD": "build a GitHub Actions pipeline on a personal project",
    "Git": "practice branching, rebasing, and pull-request workflows",
    "SQL": "master joins, aggregations, window functions, and query plans",
    "PostgreSQL": "go deep on indexing, EXPLAIN ANALYZE, and ACID guarantees",
    "MongoDB": "study the document model, aggregation pipeline, and indexing",
    "Redis": "explore caching, pub/sub, rate limiting, and sorted sets",
    "FastAPI": "build a typed REST API with Pydantic models and async endpoints",
    "Flask": "create a Flask app with blueprints, SQLAlchemy, and REST endpoints",
    "Django": "follow the official tutorial; build a CRUD app with the ORM and admin",
    "React": "build projects using hooks, context, and component patterns",
    "TypeScript": "retrofit TypeScript into a JS project; practice typed interfaces",
    "Node.js": "build a Node.js API; master the event loop and async/await patterns",
    "TensorFlow": "work through official tutorials; train a classification model end-to-end",
    "PyTorch": "implement a neural network from scratch to understand autograd",
    "Scikit-learn": "practice full ML pipelines: preprocessing, model selection, CV",
    "NLP": "study tokenization, embeddings, attention mechanisms, and transformers",
    "Spark": "learn PySpark DataFrames, lazy evaluation, and distributed query plans",
    "Kafka": "study producers, consumers, topics, and stream-processing patterns",
    "Elasticsearch": "index and query documents; learn mappings, scoring, and aggregations",
    "Linux": "practise CLI fundamentals: file system, processes, and shell scripting",
    "Microservices": "design a microservices system; study service discovery and API gateways",
    "GraphQL": "replace a REST endpoint with GraphQL; learn schema definition and resolvers",
    "Spring Boot": "build a Spring Boot REST service with JPA and Spring Security",
    "Java": "strengthen generics, concurrency, streams, and JVM performance tuning",
    "Ansible": "automate server configuration with playbooks and roles",
    "Prometheus": "instrument an app with metrics; build Grafana dashboards on top",
}

# ---------------------------------------------------------------------------
# Category skill sets for domain-level gap detection
# ---------------------------------------------------------------------------

_CLOUD: Set[str] = {
    "AWS", "Azure", "GCP", "Firebase", "Heroku", "DigitalOcean",
    "AWS Lambda", "AWS EC2", "AWS S3", "SageMaker", "Vercel", "Netlify",
}
_DEVOPS: Set[str] = {
    "Docker", "Kubernetes", "Jenkins", "CI/CD", "Terraform", "Ansible",
    "Helm", "GitHub Actions", "GitLab CI", "CircleCI", "Travis CI",
    "Prometheus", "Grafana",
}
_ML: Set[str] = {
    "TensorFlow", "PyTorch", "Keras", "Scikit-learn", "XGBoost", "LightGBM",
    "NLP", "Deep Learning", "Machine Learning", "BERT", "GPT", "Hugging Face",
    "Transformers", "LangChain", "FAISS", "Sentence Transformers",
}
_WEB: Set[str] = {
    "React", "Angular", "Vue.js", "Next.js", "Node.js", "Django", "Flask",
    "FastAPI", "Express.js", "GraphQL", "TypeScript", "Svelte", "Nuxt.js",
}
_DB: Set[str] = {
    "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Elasticsearch",
    "Cassandra", "DynamoDB", "SQLite", "Neo4j", "ClickHouse", "Snowflake",
}

_CATEGORY_TIPS: Dict[str, str] = {
    "cloud": (
        "Focus on one cloud provider — pick AWS, Azure, or GCP and earn a "
        "practitioner-level certification to demonstrate cloud fundamentals."
    ),
    "devops": (
        "Build a DevOps skill chain: Docker containerisation → Kubernetes "
        "orchestration → CI/CD pipeline automation with GitHub Actions."
    ),
    "ml": (
        "Deepen ML engineering: go beyond training to model evaluation, "
        "deployment, monitoring, and basic MLOps practices."
    ),
    "web": (
        "Pick a modern frontend framework (React or Vue) and pair it with "
        "a backend API framework (FastAPI or Django) for full-stack coverage."
    ),
    "database": (
        "Cover relational SQL deeply (joins, indexes, transactions) plus "
        "one NoSQL store (MongoDB or Redis) for document/cache use cases."
    ),
}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SemanticMatch:
    """A JD skill covered by a semantically similar (but not identical) resume skill."""
    resume_skill: str
    jd_skill: str
    similarity: float


@dataclass
class MatchResult:
    """Complete output of a resume ↔ JD comparison. Designed to be serialisable."""

    resume_skills: List[str]
    jd_skills: List[str]
    exact_matches: List[str]
    semantic_matches: List[SemanticMatch]
    missing_skills: List[str]       # JD skills with no resume coverage at all
    partially_matched: List[str]    # JD skills covered semantically (not exactly)
    match_score: float              # 0.0–1.0 weighted score
    confidence: str                 # "high" | "medium" | "low"
    recommendations: List[str]

    def to_dict(self) -> dict:
        """
        JSON-serialisable representation.
        Ready for REST API responses, Streamlit state, or file persistence.
        """
        return {
            "resume_skill_count": len(self.resume_skills),
            "jd_skill_count": len(self.jd_skills),
            "match_score": self.match_score,
            "match_score_pct": f"{self.match_score * 100:.1f}%",
            "confidence": self.confidence,
            "exact_matches": self.exact_matches,
            "semantic_matches": [
                {
                    "resume_skill": m.resume_skill,
                    "jd_skill": m.jd_skill,
                    "similarity": m.similarity,
                }
                for m in self.semantic_matches
            ],
            "missing_skills": self.missing_skills,
            "partially_matched": self.partially_matched,
            "recommendations": self.recommendations,
        }


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _norm_map(skills: List[str]) -> Dict[str, str]:
    """Return {normalised_key: canonical_skill} for O(1) case-insensitive lookup."""
    return {normalize_skill_name(s): s for s in skills}


def _exact_match(
    resume_skills: List[str],
    jd_skills: List[str],
) -> Tuple[List[str], List[str], List[str]]:
    """
    Case-insensitive exact matching.

    Returns:
        matched          — JD skills found in resume (resume's canonical casing)
        unmatched_resume — resume skills not consumed by any exact match
        unmatched_jd     — JD skills not found in resume
    """
    resume_map = _norm_map(resume_skills)
    jd_map = _norm_map(jd_skills)

    matched: List[str] = []
    unmatched_jd: List[str] = []

    for norm_key, canonical_jd in jd_map.items():
        if norm_key in resume_map:
            matched.append(resume_map[norm_key])
        else:
            unmatched_jd.append(canonical_jd)

    matched_norm = {normalize_skill_name(s) for s in matched}
    unmatched_resume = [s for s in resume_skills if normalize_skill_name(s) not in matched_norm]

    return matched, unmatched_resume, unmatched_jd


def _semantic_match(
    unmatched_resume: List[str],
    unmatched_jd: List[str],
    threshold: float,
) -> Tuple[List[SemanticMatch], List[str]]:
    """
    For each unmatched JD skill find the closest resume skill via cosine similarity.
    Skills above `threshold` are considered semantically covered.

    Returns:
        matches        — SemanticMatch instances for covered JD skills
        still_missing  — JD skills with no resume coverage above threshold
    """
    if not unmatched_resume or not unmatched_jd:
        return [], unmatched_jd

    resume_embs = get_skill_embeddings(unmatched_resume)
    jd_embs = get_skill_embeddings(unmatched_jd)
    index = build_skill_index(resume_embs)

    matches: List[SemanticMatch] = []
    still_missing: List[str] = []

    for i, jd_skill in enumerate(unmatched_jd):
        q = jd_embs[i : i + 1]
        scores, idxs = index.search(q, 1)  # type: ignore[call-arg]
        top_score = float(scores[0][0])
        top_idx = int(idxs[0][0])

        if top_idx >= 0 and top_score >= threshold:
            matches.append(SemanticMatch(
                resume_skill=unmatched_resume[top_idx],
                jd_skill=jd_skill,
                similarity=round(top_score, 3),
            ))
        else:
            still_missing.append(jd_skill)

    return matches, still_missing


def _weighted_score(
    exact: List[str],
    semantic: List[SemanticMatch],
    total_jd: int,
) -> float:
    """
    Weighted coverage score:
      exact match   → 1.0 weight per JD skill
      semantic match → SEMANTIC_MATCH_WEIGHT × cosine_similarity

    Clamped to [0.0, 1.0].
    """
    if total_jd == 0:
        return 0.0
    exact_pts = float(len(exact))
    semantic_pts = sum(m.similarity * SEMANTIC_MATCH_WEIGHT for m in semantic)
    return min((exact_pts + semantic_pts) / total_jd, 1.0)


def _confidence_label(jd_skill_count: int) -> str:
    if jd_skill_count >= _HIGH_CONFIDENCE_MIN_JD_SKILLS:
        return "high"
    if jd_skill_count >= _MEDIUM_CONFIDENCE_MIN_JD_SKILLS:
        return "medium"
    return "low"


def _recommendations(
    missing: List[str],
    semantic: List[SemanticMatch],
) -> List[str]:
    """
    Generate prioritised, actionable recommendations.

    Priority order:
    1. Per-skill tips for each missing skill that has a known tip.
    2. Visibility tips for semantic matches below 90% — candidate has the
       skill but uses a different name; they should surface it more clearly.
    3. Category-level guidance when ≥ 2 skills from the same domain are missing.
    """
    recs: List[str] = []
    missing_set = set(missing)
    covered_categories: Set[str] = set()

    for skill in missing:
        if skill in _SKILL_TIPS:
            recs.append(f"Learn {skill}: {_SKILL_TIPS[skill]}")
        else:
            recs.append(f"Add {skill} to your skill set — it is listed as a requirement")

    for m in semantic:
        if m.similarity < 0.90:
            recs.append(
                f"Highlight '{m.resume_skill}' more explicitly — "
                f"the JD asks for '{m.jd_skill}' ({m.similarity:.0%} semantic match)"
            )

    for cat, skill_set, tip in [
        ("cloud",    _CLOUD,  _CATEGORY_TIPS["cloud"]),
        ("devops",   _DEVOPS, _CATEGORY_TIPS["devops"]),
        ("ml",       _ML,     _CATEGORY_TIPS["ml"]),
        ("web",      _WEB,    _CATEGORY_TIPS["web"]),
        ("database", _DB,     _CATEGORY_TIPS["database"]),
    ]:
        if len(missing_set & skill_set) >= 2 and cat not in covered_categories:
            recs.append(tip)
            covered_categories.add(cat)

    return recs


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def score_match(
    resume_skills: List[str],
    jd_skills: List[str],
    semantic_threshold: float = SEMANTIC_MATCH_THRESHOLD,
) -> MatchResult:
    """
    Compare resume skills against JD skills and return a complete MatchResult.

    Two-pass matching strategy:
      Pass 1 — Exact (case-insensitive): full credit per matched JD skill.
      Pass 2 — Semantic (cosine ≥ threshold): partial credit via SEMANTIC_MATCH_WEIGHT.

    The taxonomy-based extraction in rag_pipeline/skill_extractor already
    normalises most synonyms (NLP ↔ Natural Language Processing, etc.),
    so semantic pass catches genuine near-misses and aliased skill names.

    Args:
        resume_skills:      Canonical skills extracted from the candidate's resume.
        jd_skills:          Canonical skills extracted from the job description.
        semantic_threshold: Cosine similarity floor for a semantic match (default 0.80).

    Returns:
        MatchResult — serialisable via .to_dict(), ready for any frontend.
    """
    if not jd_skills:
        return MatchResult(
            resume_skills=resume_skills,
            jd_skills=[],
            exact_matches=[],
            semantic_matches=[],
            missing_skills=[],
            partially_matched=[],
            match_score=0.0,
            confidence="low",
            recommendations=["No skills detected in the job description — check the JD text."],
        )

    exact, unmatched_resume, unmatched_jd = _exact_match(resume_skills, jd_skills)
    semantic, missing = _semantic_match(unmatched_resume, unmatched_jd, semantic_threshold)

    score = _weighted_score(exact, semantic, len(jd_skills))
    confidence = _confidence_label(len(jd_skills))
    recs = _recommendations(missing, semantic)

    return MatchResult(
        resume_skills=resume_skills,
        jd_skills=jd_skills,
        exact_matches=sorted(exact),
        semantic_matches=sorted(semantic, key=lambda m: -m.similarity),
        missing_skills=sorted(missing),
        partially_matched=[m.jd_skill for m in semantic],
        match_score=round(score, 4),
        confidence=confidence,
        recommendations=recs,
    )
