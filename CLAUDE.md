# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

AI Career Copilot — RAG pipeline for resume skill extraction + semantic Resume ↔ JD matching with gap analysis and recommendations.

## Setup & Commands

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Resume skill extraction only
python app/rag_pipeline.py [resume.pdf]

# Full Resume ↔ JD matching (uses built-in example JD)
python -m app.jd_matcher

# With a custom resume and JD text file
python -m app.jd_matcher data/resume.pdf data/job_posting.txt
```

No test runner, linter, or build system is configured yet.

## Architecture

```
ai_career_copilot/
├── app/
│   ├── __init__.py          — package marker
│   ├── rag_pipeline.py      — PDF loading, OCR, chunking, FAISS, skill extraction
│   ├── skill_extractor.py   — text-based skill extraction (for JDs / plain text)
│   ├── embedding_engine.py  — skill-level embedding + FAISS index helpers
│   ├── retrieval_engine.py  — FAISS retrieval pipeline for raw text documents
│   ├── scoring_engine.py    — exact/semantic matching, scoring, recommendations
│   ├── jd_matcher.py        — orchestration + CLI entry point
│   └── utils.py             — normalize, deduplicate, format utilities
├── data/
│   └── Dhaani_Jain_resume.pdf
├── models/                  — reserved for future model artifacts
└── outputs/                 — JSON match reports written here
```

**Resume extraction pipeline (`rag_pipeline.py`):**

1. **Load** — `load_pdf()` extracts text via `pdfplumber`; falls back to OCR (`pytesseract` + `pdf2image`) at 300 DPI when the text layer is sparse.
2. **OCR fix** — `normalize_ocr()` corrects misreads (`"tensor flow"` → `"tensorflow"`) before any analysis.
3. **Clean** — `clean_text()` strips PII (emails, URLs, phones) and normalises whitespace.
4. **Sections** — `extract_skill_sections()` isolates skill-bearing headings; full doc used as fallback.
5. **Chunk** — `chunk_text()` splits with deduplication via MD5 content hashing.
6. **Embed** — `embed()` encodes with `all-MiniLM-L6-v2` and L2-normalises (cosine space).
7. **Index** — `build_index()` builds an in-memory FAISS `IndexFlatIP`.
8. **Retrieve** — `retrieve_chunks()` runs multi-query retrieval with diversity filtering.
9. **Extract** — `extract_technical_skills()` uses whitelist-first extraction with confidence scoring.

**JD matching pipeline (`jd_matcher.py`):**

1. Resume skills are extracted via `run_pipeline()` from `rag_pipeline.py`.
2. JD skills are extracted via `skill_extractor.extract_skills_from_text()` — no PDF, no FAISS overhead for short texts.
3. `scoring_engine.score_match()` runs two-pass matching: exact → semantic (cosine ≥ 0.80).
4. `MatchResult` contains score, matches, gaps, and recommendations; `.to_dict()` for JSON output.
5. Report printed to terminal; JSON saved to `outputs/match_report.json`.

**Key design notes:**
- SKILL_TAXONOMY in `rag_pipeline.py` is the single source of truth for skill normalisation — extend it to support new skills; no logic changes needed elsewhere.
- FAISS index is built in-memory each run — no persistent vector store.
- All public functions accept dynamic text inputs — nothing is hardcoded in business logic.
- `MatchResult.to_dict()` is the integration contract for future Streamlit / FastAPI frontends.
