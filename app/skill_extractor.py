"""
app/skill_extractor.py — AI Career Copilot
Extracts technical skills from any raw text string (JDs, plain-text resumes).

Unlike the full PDF pipeline in rag_pipeline.py, this module:
  - Accepts a raw string directly (no PDF loading or OCR)
  - For short texts (< 1500 chars, typical JD): all chunks are processed as
    a "skill section", maximising recall with no retrieval overhead.
  - For longer texts: FAISS retrieval narrows down skill-dense regions first.

This design makes it suitable for both concise JD strings and long documents.
"""

from typing import List

from .rag_pipeline import (
    chunk_text,
    clean_text,
    extract_technical_skills,
    normalize_ocr,
)
from .retrieval_engine import retrieve_from_text

_RETRIEVAL_CHAR_THRESHOLD = 1_500  # chars above which retrieval improves precision


def extract_skills_from_text(
    text: str,
    confidence_threshold: float = 0.4,
) -> List[str]:
    """
    Extract technical skills from any raw text string.

    Two execution paths based on text length:

    Short text (< 1500 chars) — typical JD or skills section:
        All chunks are treated as a skill region (high confidence).
        No FAISS retrieval overhead needed.

    Long text (≥ 1500 chars) — text resume, article, wiki page:
        FAISS retrieval selects the most skill-dense regions first,
        improving precision on noisy long documents.

    Args:
        text: Raw input string — JD, plain-text resume, wiki excerpt, etc.
        confidence_threshold: Minimum confidence for a skill to be included.
            0.4 captures skills stated once in clean prose (good for JDs).
            Raise to 0.8 for whitelist-only, near-zero false-positive mode.

    Returns:
        Deduplicated list of canonical skill names, sorted by confidence desc.
    """
    text = normalize_ocr(text)
    text = clean_text(text)

    if len(text) < _RETRIEVAL_CHAR_THRESHOLD:
        chunks = chunk_text(text, chunk_size=400, overlap=80)
        skill_results = extract_technical_skills(
            retrieved_chunks=chunks,
            skill_section_text=text,
            confidence_threshold=confidence_threshold,
        )
    else:
        retrieved = retrieve_from_text(text)
        skill_results = extract_technical_skills(
            retrieved_chunks=retrieved,
            skill_section_text="",
            confidence_threshold=confidence_threshold,
        )

    return [item["skill"] for item in skill_results]
