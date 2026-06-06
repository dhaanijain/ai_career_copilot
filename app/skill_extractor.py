"""
app/skill_extractor.py — AI Career Copilot
Extracts technical skills from any raw text string (JDs, plain-text resumes).

v2 — Four targeted fixes over v1:

  1. Delimiter normalisation
     Commas, semicolons, bullets, pipes, and parentheses are converted to
     newlines BEFORE clean_text strips them.  _process() in
     extract_technical_skills splits on newlines, so comma-separated inline
     skill lists ("Python, Docker, AWS") are now handled correctly.

  2. Sentence-boundary punctuation stripping
     clean_text keeps '.' (needed for "Node.js", "ASP.NET"), so tokens like
     "AWS." appear and don't match "aws" in SKILL_TAXONOMY.  A pre-pass
     removes trailing periods from word-final positions before clean_text.

  3. Fast direct-scan pass (_fast_scan)
     Runs on the raw, unmodified text before any cleaning.  Matches every
     key in SKILL_TAXONOMY + _JD_ALIASES using whole-word boundaries.
     Catches abbreviations (ml, tf, k8s, genai), JD-specific phrasing, and
     any skills that chunking boundaries or diversity filtering might miss.

  4. _JD_ALIASES — extensible alias table
     Maps JD abbreviations and phrasing variants that are absent from
     rag_pipeline's SKILL_TAXONOMY (ml→Machine Learning, tf→TensorFlow,
     rag→RAG, mlops→MLOps, genai→Generative AI, etc.).

  Additionally: _RETRIEVAL_CHAR_THRESHOLD raised to 10 000 chars so typical
  Adzuna JDs (200–3 000 chars) always use the direct full-text path, treating
  the entire document as a skill section (from_skill_section=True).  The FAISS
  retrieval path — which can drop skill-bearing chunks via diversity filtering —
  is now reserved for genuinely long corpus documents only.
"""

import re
from typing import Dict, List, Set

from .logger import get_logger
from .rag_pipeline import (
    SKILL_TAXONOMY,
    chunk_text,
    clean_text,
    extract_technical_skills,
    normalize_ocr,
)
from .retrieval_engine import retrieve_from_text

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# JD alias table
# Maps lowercase JD abbreviations and variant spellings → canonical skill name.
# Entries absent from rag_pipeline.SKILL_TAXONOMY only; no duplicates.
# Sort order does not matter here — _fast_scan sorts by length at runtime.
# ---------------------------------------------------------------------------

_JD_ALIASES: Dict[str, str] = {
    # ── AI / ML abbreviations ────────────────────────────────────────────
    "ml":                             "Machine Learning",
    "dl":                             "Deep Learning",
    "ai":                             "Artificial Intelligence",
    "tf":                             "TensorFlow",
    "gen ai":                         "Generative AI",
    "genai":                          "Generative AI",
    "generative ai":                  "Generative AI",
    "llm":                            "LLMs",
    "llms":                           "LLMs",
    "large language model":           "LLMs",
    "large language models":          "LLMs",
    "rl":                             "Reinforcement Learning",
    "cv":                             "Computer Vision",
    "nlg":                            "NLP",
    "nlu":                            "NLP",
    "ner":                            "NLP",
    "text classification":            "NLP",
    "sentiment analysis":             "NLP",
    "mlops":                          "MLOps",
    "ml ops":                         "MLOps",
    "rag":                            "RAG",
    "retrieval augmented generation": "RAG",
    "fine tuning":                    "Fine-Tuning",
    "fine-tuning":                    "Fine-Tuning",
    "finetuning":                     "Fine-Tuning",
    "prompt engineering":             "Prompt Engineering",
    "vector database":                "Vector Databases",
    "vector databases":               "Vector Databases",
    "vector db":                      "Vector Databases",
    "vector store":                   "Vector Databases",
    "embedding":                      "Embeddings",
    "embeddings":                     "Embeddings",
    "cnn":                            "CNN",
    "convolutional neural network":   "CNN",
    "rnn":                            "RNN",
    "recurrent neural network":       "RNN",
    "lstm":                           "LSTM",
    "gan":                            "GANs",
    "generative adversarial network": "GANs",
    "transfer learning":              "Transfer Learning",
    "feature engineering":            "Feature Engineering",
    "a/b testing":                    "A/B Testing",
    "ab testing":                     "A/B Testing",
    "data modelling":                 "Data Modeling",
    "data modeling":                  "Data Modeling",
    "statistical modelling":          "Statistical Modeling",
    "statistical modeling":           "Statistical Modeling",

    # ── Cloud / Infrastructure ───────────────────────────────────────────
    "gcloud":                         "GCP",
    "google cloud platform":          "GCP",
    "amazon aws":                     "AWS",
    "amazon web services":            "AWS",
    "ms azure":                       "Azure",
    "azure cloud":                    "Azure",
    "cloud computing":                "Cloud Computing",
    "cloud native":                   "Cloud Native",
    "serverless":                     "Serverless",
    "lambda function":                "AWS Lambda",
    "lambda functions":               "AWS Lambda",
    "cloud functions":                "Cloud Functions",

    # ── DevOps / CI/CD ───────────────────────────────────────────────────
    "k8":                             "Kubernetes",
    "ci cd":                          "CI/CD",
    "cicd":                           "CI/CD",
    "ci/cd pipeline":                 "CI/CD",
    "continuous integration":         "CI/CD",
    "continuous deployment":          "CI/CD",
    "continuous delivery":            "CI/CD",
    "iac":                            "Terraform",
    "infrastructure as code":         "Terraform",
    "containerization":               "Docker",
    "containerisation":               "Docker",
    "github action":                  "GitHub Actions",
    "gitlab cicd":                    "GitLab CI",
    "version control":                "Git",
    "code versioning":                "Git",

    # ── Backend / APIs ───────────────────────────────────────────────────
    "springboot":                     "Spring Boot",
    "asp net":                        "ASP.NET",
    "asp.net core":                   "ASP.NET",
    "rest api":                       "REST",
    "restful api":                    "REST",
    "restful apis":                   "REST",
    "rest apis":                      "REST",
    "api development":                "API",
    "api design":                     "API",
    "grpc":                           "gRPC",
    "message queue":                  "Message Queues",
    "message queuing":                "Message Queues",
    "rabbitmq":                       "RabbitMQ",
    "rabbit mq":                      "RabbitMQ",
    "apache kafka":                   "Kafka",
    "apache spark":                   "Spark",
    "apache airflow":                 "Airflow",
    "airflow":                        "Airflow",
    "celery":                         "Celery",
    "redis cache":                    "Redis",
    "websocket":                      "WebSockets",
    "websockets":                     "WebSockets",
    "web sockets":                    "WebSockets",

    # ── Data Engineering ─────────────────────────────────────────────────
    "pyspark":                        "Spark",
    "etl":                            "ETL",
    "elt":                            "ETL",
    "data pipeline":                  "Data Pipelines",
    "data pipelines":                 "Data Pipelines",
    "data engineering":               "Data Engineering",
    "data warehouse":                 "Data Warehousing",
    "data warehousing":               "Data Warehousing",
    "dbt":                            "dbt",
    "data build tool":                "dbt",
    "data lake":                      "Data Lakes",
    "data lakes":                     "Data Lakes",
    "batch processing":               "Batch Processing",
    "stream processing":              "Stream Processing",
    "real time processing":           "Stream Processing",
    "real-time processing":           "Stream Processing",

    # ── Databases ────────────────────────────────────────────────────────
    "rdbms":                          "SQL",
    "relational database":            "SQL",
    "relational databases":           "SQL",
    "postgres":                       "PostgreSQL",
    "mongo":                          "MongoDB",
    "elastic search":                 "Elasticsearch",

    # ── Frontend / Mobile ────────────────────────────────────────────────
    "nextjs":                         "Next.js",
    "nuxtjs":                         "Nuxt.js",
    "expressjs":                      "Express.js",
    "vuejs":                          "Vue.js",
    "angularjs":                      "Angular",
    "cross platform":                 "React Native",
    "ios development":                "iOS",
    "android development":            "Android",
    "responsive design":              "Responsive Design",
    "ui/ux":                          "UI/UX",
    "ui ux":                          "UI/UX",

    # ── Concepts / Paradigms ─────────────────────────────────────────────
    "object oriented":                "OOP",
    "object-oriented":                "OOP",
    "functional programming":         "Functional Programming",
    "tdd":                            "TDD",
    "test driven development":        "TDD",
    "bdd":                            "BDD",
    "system design":                  "System Design",
    "distributed systems":            "Distributed Systems",
    "distributed computing":          "Distributed Systems",
    "microservice":                   "Microservices",
    "micro services":                 "Microservices",
    "event driven":                   "Event-Driven Architecture",
    "event-driven":                   "Event-Driven Architecture",
    "solid principles":               "SOLID",
    "design patterns":                "Design Patterns",
    "data structures and algorithms": "Data Structures",
    "dsa":                            "Data Structures",

    # ── Testing ──────────────────────────────────────────────────────────
    "unit testing":                   "Unit Testing",
    "unit test":                      "Unit Testing",
    "integration testing":            "Integration Testing",
    "pytest":                         "PyTest",
    "jest":                           "Jest",
    "junit":                          "JUnit",
    "selenium":                       "Selenium",
    "cypress":                        "Cypress",
    "end to end testing":             "E2E Testing",
    "e2e testing":                    "E2E Testing",

    # ── Security ─────────────────────────────────────────────────────────
    "oauth":                          "OAuth",
    "jwt":                            "JWT",
    "json web token":                 "JWT",
    "owasp":                          "OWASP",
    "penetration testing":            "Penetration Testing",
    "pen testing":                    "Penetration Testing",
    "cybersecurity":                  "Cybersecurity",

    # ── Analytics / BI ───────────────────────────────────────────────────
    "tableau":                        "Tableau",
    "power bi":                       "Power BI",
    "powerbi":                        "Power BI",
    "looker":                         "Looker",
    "metabase":                       "Metabase",
    "data visualization":             "Data Visualization",
    "data visualisation":             "Data Visualization",
    "business intelligence":          "Business Intelligence",
}

# Pre-sorted by key length (longest first) so multi-word phrases match before
# their substrings do.  Built once at import time for performance.
_ALIAS_KEYS_SORTED: List[str] = sorted(_JD_ALIASES.keys(), key=len, reverse=True)

# Union of all recognised canonical skill names from both sources.
# Used to reject short all-caps tokens produced by the unknown-token
# heuristic when '/' splits compound names (e.g. "CI/CD" → "CI" + "CD").
_KNOWN_CANONICAL: Set[str] = set(SKILL_TAXONOMY.values()) | set(_JD_ALIASES.values())

# Delimiter characters that separate skills in JD prose.
# Converted to newlines before clean_text, so _process() can split on them.
_DELIMITER_RE = re.compile(r"[,;|•·●◦▪▸►()\[\]]")

# Matches any period followed by whitespace or end-of-string — these are
# sentence/clause boundaries that clean_text keeps (because '.' is needed
# for "Node.js") but that break token lookup ("AWS." doesn't match "aws").
# Mid-word periods like "Node.js", "ASP.NET", "v1.2" are safe because they
# are followed by alphanumeric characters, not whitespace.
_SENTENCE_PERIOD_RE = re.compile(r"\.(?=\s|$)", re.MULTILINE)

# Short, ambiguous words that are common English verbs/words — excluded from
# fast scan to avoid false positives (e.g. "go" as a verb matching Go).
_AMBIGUOUS_KEYS: Set[str] = {"go", "r", "c", "rust"}

# Minimum key length for fast scan.  Single-char keys ("r", "c") are handled
# by the chunk-based pass which has more context.
_MIN_SCAN_KEY_LEN = 2

# Below this char count, the full text is treated as a skill section (direct
# path).  Typical Adzuna JDs are 200–3 000 chars; raising this to 10 000
# means all JDs use the direct path and avoid FAISS diversity filtering.
_RETRIEVAL_CHAR_THRESHOLD = 10_000


# ---------------------------------------------------------------------------
# Pre-processing helpers
# ---------------------------------------------------------------------------

def _filter_noise(skills: List[str]) -> List[str]:
    """
    Remove short all-caps tokens that the unknown-token heuristic in
    extract_technical_skills generates when _process() splits compound skill
    names on '/'.  Example: 'CI/CD' → ['CI', 'CD'] → 'CI' passes the
    heuristic (uppercase, short, not in NON_SKILL_WORDS) but is not a skill.

    A token is treated as noise when ALL of:
      - all uppercase (artefact of a split, not a full acronym like "NLP")
      - 2 chars or fewer
      - not a recognised canonical skill name
    """
    return [
        s for s in skills
        if not (s.isupper() and len(s) <= 2 and s not in _KNOWN_CANONICAL)
    ]


def _strip_sentence_punct(text: str) -> str:
    """
    Remove sentence-boundary periods before clean_text so that skill tokens
    like "AWS." become "AWS" and match SKILL_TAXONOMY correctly.
    Mid-word periods (Node.js, ASP.NET, e.g.) are intentionally left intact.
    """
    return _SENTENCE_PERIOD_RE.sub(" ", text)


def _normalise_delimiters(text: str) -> str:
    """
    Convert skill-list separator characters (commas, bullets, pipes, parens)
    to newlines before clean_text strips them.  clean_text preserves newlines,
    and _process() in extract_technical_skills splits on them — so this
    recovers the comma-separated structure common in JD prose.
    """
    return _DELIMITER_RE.sub("\n", text)


# ---------------------------------------------------------------------------
# Fast direct-scan pass
# ---------------------------------------------------------------------------

def _fast_scan(raw_text: str) -> List[str]:
    """
    Scan raw, uncleaned text for every key in SKILL_TAXONOMY + _JD_ALIASES
    using whole-word boundary matching.

    Why run on raw text:
    - Catches abbreviations (ml, tf, k8s) before clean_text normalises them.
    - Not blocked by chunking boundaries or FAISS diversity filtering.
    - Handles JD-specific phrasing absent from SKILL_TAXONOMY.

    Multi-word phrases are checked before single-word keys (sorted by length
    descending) so "machine learning" is found before "machine".

    Returns skills in order of first appearance in the text.
    """
    text_lower = raw_text.lower()
    found: Dict[str, int] = {}  # canonical → first match position

    # SKILL_TAXONOMY keys — longest first
    for key in sorted(SKILL_TAXONOMY.keys(), key=len, reverse=True):
        if len(key) < _MIN_SCAN_KEY_LEN or key in _AMBIGUOUS_KEYS:
            continue
        m = re.search(r"\b" + re.escape(key) + r"\b", text_lower)
        if m:
            canonical = SKILL_TAXONOMY[key]
            if canonical not in found:
                found[canonical] = m.start()

    # _JD_ALIASES — longest first
    for key in _ALIAS_KEYS_SORTED:
        if len(key) < _MIN_SCAN_KEY_LEN or key in _AMBIGUOUS_KEYS:
            continue
        m = re.search(r"\b" + re.escape(key) + r"\b", text_lower)
        if m:
            canonical = _JD_ALIASES[key]
            if canonical not in found:
                found[canonical] = m.start()

    return [skill for skill, _ in sorted(found.items(), key=lambda x: x[1])]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def extract_skills_from_text(
    text: str,
    confidence_threshold: float = 0.4,
) -> List[str]:
    """
    Extract technical skills from any raw text string (JD, plain-text resume).

    Two-pass hybrid pipeline:

    Pass 1 — Fast direct scan (_fast_scan):
        Whole-word regex search against SKILL_TAXONOMY + _JD_ALIASES on the
        raw text.  Catches abbreviations (ml→Machine Learning, tf→TensorFlow),
        JD-specific phrases (rag, mlops, genai), and inline mentions that
        chunking or FAISS diversity filtering might otherwise miss.

    Pass 2 — Chunk-based extraction (extract_technical_skills):
        Pre-processes text with four steps before the rag_pipeline pass:
          a. normalize_ocr  — corrects OCR misreads
          b. _strip_sentence_punct — removes trailing "." from skill tokens
             so "AWS." matches "aws" in SKILL_TAXONOMY
          c. _normalise_delimiters — converts commas/bullets/parens to \\n
             so _process() can split comma-separated skill lists correctly
          d. clean_text  — strips PII and normalises whitespace
        Full JD text (up to 10 000 chars) is always treated as a skill
        section (from_skill_section=True, confidence 1.0 for whitelist hits).

    Results are merged with case-insensitive deduplication; Pass 1 skills
    appear first (inline occurrence order), followed by any new skills found
    only by Pass 2.

    Args:
        text:                 Raw string — JD, plain-text resume, etc.
        confidence_threshold: Minimum confidence for Pass 2 results.
                              0.4 is appropriate for JD text.

    Returns:
        Deduplicated list of canonical skill names.
    """
    if not text or not text.strip():
        log.warning("extract_skills_from_text called with empty text")
        return []

    log.info("extract_skills_from_text: input length=%d chars, confidence_threshold=%.2f", len(text), confidence_threshold)

    # ── Pass 1: fast scan on raw text ────────────────────────────────────────
    fast_skills = _fast_scan(text)
    log.debug("Pass 1 (fast scan) found %d skills: %s", len(fast_skills), fast_skills)

    # ── Pre-processing for Pass 2 ─────────────────────────────────────────────
    # Order matters: delimiter normalisation first converts "(Lambda)." →
    # "Lambda\n." so the subsequent period strip catches the isolated "."
    # that would otherwise produce ". CI" false positives when split on "/".
    proc = normalize_ocr(text)
    proc = _normalise_delimiters(proc)
    proc = _strip_sentence_punct(proc)
    proc = clean_text(proc)

    if not proc.strip():
        log.warning("Text became empty after pre-processing; returning Pass 1 results only")
        return fast_skills

    # ── Pass 2: chunk-based extraction ────────────────────────────────────────
    if len(proc) < _RETRIEVAL_CHAR_THRESHOLD:
        log.info("Pass 2: direct path (text length %d < threshold %d)", len(proc), _RETRIEVAL_CHAR_THRESHOLD)
        chunks = chunk_text(proc, chunk_size=400, overlap=80)
        log.debug("Pass 2: %d chunks produced", len(chunks))
        skill_results = extract_technical_skills(
            retrieved_chunks=chunks,
            skill_section_text=proc,   # full JD = one big skill section
            confidence_threshold=confidence_threshold,
        )
    else:
        # Genuinely long document: FAISS retrieval + first 3 000 chars as
        # a high-confidence skill section to catch leading requirements.
        log.info("Pass 2: FAISS retrieval path (text length %d >= threshold %d)", len(proc), _RETRIEVAL_CHAR_THRESHOLD)
        retrieved = retrieve_from_text(proc)
        log.debug("Pass 2: FAISS retrieved %d chunks", len(retrieved))
        skill_results = extract_technical_skills(
            retrieved_chunks=retrieved,
            skill_section_text=proc[:3_000],
            confidence_threshold=confidence_threshold,
        )

    pipeline_skills = _filter_noise([item["skill"] for item in skill_results])
    log.debug("Pass 2 (chunk-based) found %d skills after noise filter: %s", len(pipeline_skills), pipeline_skills)

    # ── Merge: dedup preserving Pass 1 order ─────────────────────────────────
    seen: Set[str] = {s.lower().strip() for s in fast_skills}
    merged: List[str] = list(fast_skills)
    for skill in pipeline_skills:
        if skill.lower().strip() not in seen:
            seen.add(skill.lower().strip())
            merged.append(skill)

    log.info("extract_skills_from_text: merged result %d skills: %s", len(merged), merged)
    return merged


# ---------------------------------------------------------------------------
# Test cases (run with: python -m app.skill_extractor)
# ---------------------------------------------------------------------------

_TEST_CASES = {
    "abbreviations": (
        "We need an ML engineer with DL, NLP, CV and RL experience. AI background preferred.",
        ["Machine Learning", "Deep Learning", "NLP", "Computer Vision",
         "Reinforcement Learning", "Artificial Intelligence"],
    ),
    "inline_prose": (
        "Build and deploy models using TF and sklearn in our k8s cluster on AWS.",
        ["TensorFlow", "Scikit-learn", "Kubernetes", "AWS"],
    ),
    "comma_separated": (
        "Required skills: Python, TensorFlow, PyTorch, Docker, AWS, SQL, NLP, Kubernetes.",
        ["Python", "TensorFlow", "PyTorch", "Docker", "AWS", "SQL", "NLP", "Kubernetes"],
    ),
    "slash_separated": (
        "Skills: Python/TensorFlow/PyTorch/AWS/Docker/Kubernetes",
        ["Python", "TensorFlow", "PyTorch", "AWS", "Docker", "Kubernetes"],
    ),
    "parentheses": (
        "Cloud experience (AWS, GCP, Azure) and containers (Docker, k8s) required.",
        ["AWS", "GCP", "Azure", "Docker", "Kubernetes"],
    ),
    "jd_phrases": (
        "Proficiency in gen ai, llms, rag pipelines, vector databases, and mlops.",
        ["Generative AI", "LLMs", "RAG", "Vector Databases", "MLOps"],
    ),
    "trailing_punct": (
        "Must know Python. Strong knowledge of AWS. Docker experience is a plus.",
        ["Python", "AWS", "Docker"],
    ),
    "ocr_noise": (
        "Experience with Tensor Flow, Py Torch, Scikit Learn, and Kub ernetes required.",
        ["TensorFlow", "PyTorch", "Scikit-learn", "Kubernetes"],
    ),
    "mixed_real_world": (
        "We are looking for an ML Engineer to work on NLP and CV tasks using Python, "
        "TensorFlow/PyTorch. Deploy models via Docker on AWS (EC2, S3, Lambda). "
        "CI/CD with GitHub Actions. PostgreSQL and MongoDB for data storage. "
        "Experience with LLMs, RAG, and prompt engineering is a strong plus.",
        ["Machine Learning", "NLP", "Computer Vision", "Python",
         "TensorFlow", "PyTorch", "Docker", "AWS", "CI/CD",
         "GitHub Actions", "PostgreSQL", "MongoDB", "LLMs", "RAG", "Prompt Engineering"],
    ),
}


if __name__ == "__main__":
    bar = "=" * 62
    print(f"\n{bar}")
    print("  skill_extractor -- Extraction Quality Test Suite")
    print(bar)

    passed = 0
    for name, (jd_text, expected) in _TEST_CASES.items():
        extracted = extract_skills_from_text(jd_text)
        extracted_set = {s.lower() for s in extracted}
        expected_set = {s.lower() for s in expected}
        misses = expected_set - extracted_set

        status = "PASS" if not misses else "PARTIAL"
        if not misses:
            passed += 1

        print(f"\n  [{status}] {name}")
        print(f"    Extracted : {extracted}")
        if misses:
            print(f"    Missing   : {sorted(misses)}")

    print(f"\n{'-' * 62}")
    print(f"  Results: {passed}/{len(_TEST_CASES)} test cases fully passed")
    print(f"{bar}\n")
