"""
app/jd_matcher.py — AI Career Copilot
Orchestrates the full Resume ↔ JD matching pipeline and renders the CLI report.

Usage (from the project root):
    python -m app.jd_matcher                          # example JD, default resume
    python -m app.jd_matcher data/resume.pdf          # custom resume
    python -m app.jd_matcher data/resume.pdf jd.txt   # JD loaded from a text file

The match result is also saved to outputs/match_report.json for downstream use
(Streamlit, REST API, analytics, etc.).
"""

import json
import os
import sys
from typing import List

from .logger import get_logger, log_file_path
from .rag_pipeline import run_pipeline
from .scoring_engine import MatchResult, score_match
from .skill_extractor import extract_skills_from_text

log = get_logger(__name__)

# ---------------------------------------------------------------------------
# Hardcoded example JD — swap for sys.argv, textarea input, or an API response
# ---------------------------------------------------------------------------
_EXAMPLE_JD: str = """
We are looking for a Machine Learning Engineer Intern with hands-on experience in:
Python, TensorFlow, PyTorch, SQL, Docker, Kubernetes, AWS, Git, and NLP.
Experience with REST APIs, FastAPI, and cloud deployment is a strong plus.
Familiarity with data pipelines, feature engineering, and model deployment required.
Knowledge of CI/CD practices and containerization is highly beneficial.
"""


# ---------------------------------------------------------------------------
# Public API — all functions accept dynamic text; nothing is hardcoded here
# ---------------------------------------------------------------------------

def parse_jd(jd_text: str, confidence_threshold: float = 0.4) -> List[str]:
    """
    Extract technical skills from raw job description text.

    Uses a lower confidence threshold than resume extraction (0.4 vs 0.5)
    because JDs state required skills explicitly in clean prose, producing
    fewer false positives at this threshold.

    Args:
        jd_text: Raw JD string — from a textarea, file read, or API response.
        confidence_threshold: Minimum extraction confidence (0.0–1.0).

    Returns:
        List of canonical skill names found in the JD.
    """
    return extract_skills_from_text(jd_text, confidence_threshold=confidence_threshold)


def match_resume_to_jd(
    resume_path: str,
    jd_text: str,
    resume_confidence: float = 0.5,
    jd_confidence: float = 0.4,
    semantic_threshold: float = 0.80,
) -> MatchResult:
    """
    Full pipeline: extract skills from the resume PDF, extract skills from JD
    text, then score the match with exact and semantic comparison.

    Designed for reuse from any calling context — Streamlit, FastAPI, CLI, or
    batch job — by accepting dynamic inputs and returning a serialisable result.

    Args:
        resume_path:        Path to the candidate's PDF resume.
        jd_text:            Raw job description string.
        resume_confidence:  Confidence floor for resume skill extraction.
        jd_confidence:      Confidence floor for JD skill extraction.
        semantic_threshold: Cosine similarity floor for a semantic match.

    Returns:
        MatchResult — call .to_dict() for a JSON-serialisable representation.
    """
    log.info(
        "=== match_resume_to_jd START: resume='%s', resume_conf=%.2f, jd_conf=%.2f, semantic_threshold=%.2f ===",
        resume_path, resume_confidence, jd_confidence, semantic_threshold,
    )
    print(f"\n{'═' * 62}")
    print(f"{'  AI Career Copilot — Resume vs JD Analysis':^62}")
    print(f"{'═' * 62}")

    print("\n📄  [1/3] Extracting resume skills via RAG pipeline...")
    log.info("[1/3] Extracting resume skills from '%s'", resume_path)
    resume_skills = run_pipeline(resume_path, confidence_threshold=resume_confidence)
    log.info("[1/3] Resume skills (%d): %s", len(resume_skills), resume_skills)
    print(f"\n      ✓ Resume skills extracted: {len(resume_skills)}")

    print("\n📋  [2/3] Parsing job description skills...")
    log.info("[2/3] Parsing JD skills (jd_text length=%d chars)", len(jd_text))
    jd_skills = parse_jd(jd_text, confidence_threshold=jd_confidence)
    log.info("[2/3] JD skills (%d): %s", len(jd_skills), jd_skills)
    print(f"      ✓ JD skills detected      : {len(jd_skills)}")

    print("\n⚙   [3/3] Running scoring engine...")
    log.info("[3/3] Running scoring engine")
    result = score_match(resume_skills, jd_skills, semantic_threshold=semantic_threshold)
    log.info(
        "[3/3] Scoring complete: score=%.4f, confidence=%s, exact=%d, semantic=%d, missing=%d",
        result.match_score, result.confidence,
        len(result.exact_matches), len(result.semantic_matches), len(result.missing_skills),
    )
    print(f"      ✓ Scoring complete")

    log.info("=== match_resume_to_jd END ===")
    return result


def save_report(result: MatchResult, output_dir: str = "outputs") -> str:
    """
    Persist the MatchResult as JSON in output_dir for downstream consumption.

    Returns:
        Absolute path of the written file.
    """
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, "match_report.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
    return os.path.abspath(out_path)


# ---------------------------------------------------------------------------
# CLI rendering
# ---------------------------------------------------------------------------

def _wrap(text: str, width: int = 55) -> List[str]:
    """Word-wrap `text` at `width` chars. Returns list of lines."""
    words = text.split()
    lines: List[str] = []
    buf: List[str] = []
    for word in words:
        if len(" ".join(buf + [word])) > width:
            lines.append(" ".join(buf))
            buf = [word]
        else:
            buf.append(word)
    if buf:
        lines.append(" ".join(buf))
    return lines


def print_report(result: MatchResult, width: int = 62) -> None:
    """Render a structured, human-readable match report to stdout."""
    pct = result.match_score * 100
    bar_filled = int(pct / 5)
    bar = "█" * bar_filled + "░" * (20 - bar_filled)
    inner = width - 4

    print(f"\n{'═' * width}")
    print(f"{'  MATCH REPORT':^{width}}")
    print(f"{'═' * width}\n")

    print(f"  Resume skills  : {len(result.resume_skills)}")
    print(f"  JD skills      : {len(result.jd_skills)}")
    print(f"  Confidence     : {result.confidence}")
    print(f"\n  Match Score    : {pct:.1f}%")
    print(f"  [{bar}]")

    # ── Exact Matches ─────────────────────────────────────────
    print(f"\n  {'─' * inner}")
    print(f"  Matching Skills  ({len(result.exact_matches)})")
    print(f"  {'─' * inner}")
    if result.exact_matches:
        for s in result.exact_matches:
            print(f"    ✅  {s}")
    else:
        print("    (none)")

    # ── Semantic Matches ──────────────────────────────────────
    if result.semantic_matches:
        print(f"\n  {'─' * inner}")
        print(f"  Semantic Matches  ({len(result.semantic_matches)})  — similar, not identical")
        print(f"  {'─' * inner}")
        for m in result.semantic_matches:
            print(f"    ≈  {m.resume_skill}  ↔  {m.jd_skill}  ({m.similarity:.0%})")

    # ── Missing Skills ────────────────────────────────────────
    print(f"\n  {'─' * inner}")
    print(f"  Missing Skills  ({len(result.missing_skills)})")
    print(f"  {'─' * inner}")
    if result.missing_skills:
        for s in result.missing_skills:
            print(f"    ❌  {s}")
    else:
        print("    Full JD coverage — no gaps detected!")

    # ── Recommendations ───────────────────────────────────────
    print(f"\n  {'─' * inner}")
    print(f"  Recommendations")
    print(f"  {'─' * inner}")
    if result.recommendations:
        for i, rec in enumerate(result.recommendations, 1):
            lines = _wrap(rec, width=55)
            print(f"    {i}. {lines[0]}")
            for cont in lines[1:]:
                print(f"       {cont}")
    else:
        print("    Great fit — no major gaps detected!")

    print(f"\n{'═' * width}\n")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print(f"  Log file → {log_file_path()}")
    log.info("CLI invoked with args: %s", sys.argv)

    _resume_path: str = (
        sys.argv[1] if len(sys.argv) > 1 else "data/Dhaani_Jain_resume.pdf"
    )

    if len(sys.argv) > 2:
        with open(sys.argv[2], encoding="utf-8") as _f:
            _jd_text: str = _f.read()
    else:
        _jd_text = _EXAMPLE_JD

    try:
        _result = match_resume_to_jd(_resume_path, _jd_text)
        print_report(_result)

        _saved = save_report(_result)
        log.info("Report saved to %s", _saved)
        print(f"  Report saved → {_saved}\n")
    except Exception as _exc:
        log.error("Fatal error during pipeline execution", exc_info=True)
        print(f"\n  ERROR: {_exc}")
        print(f"  Full traceback written to: {log_file_path()}")
        sys.exit(1)
