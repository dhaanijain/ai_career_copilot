# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Purpose

AI Career Copilot — currently implements a RAG pipeline to extract technical skills from PDF resumes using semantic search and NLP.

## Setup & Commands

```bash
# Activate virtual environment (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python app/rag_pipeline.py
```

No test runner, linter, or build system is configured yet.

## Architecture

The entire pipeline lives in `app/rag_pipeline.py` as a sequence of functions operating on a single PDF resume (`data/Dhaani_Jain_resume.pdf`).

**Data flow:**

1. **Load** — `load_pdf()` extracts text via `pdfplumber`; falls back to OCR (`pytesseract` + `pdf2image`) when extracted text is sparse (<50 chars).
2. **Clean** — `clean_text()` normalizes whitespace and removes special characters.
3. **Chunk** — `chunk_text()` splits text into 500-char chunks with 100-char overlap using LangChain's `RecursiveCharacterTextSplitter`.
4. **Filter sections** — `filter_skill_chunks()` keeps only chunks containing skill-related keywords, so the vector search is scoped to the relevant parts of the resume.
5. **Embed** — `create_embeddings()` encodes chunks with `sentence-transformers` (`all-MiniLM-L6-v2`).
6. **Index** — `create_faiss_index()` builds an in-memory FAISS L2 index from the embeddings.
7. **Retrieve** — `retrieve_chunks()` encodes a fixed query string and fetches the top-5 most similar chunks.
8. **Extract** — `extract_skills()` uses regex + keyword matching with OCR-correction rules (e.g., `"openal"` → `"OpenAI"`) and proper-casing for known skill names.
9. **Filter technical** — `filter_technical_skills()` removes soft-skill words (team, communication, leadership, etc.).

**Key design notes:**
- FAISS index is built in-memory each run — there is no persistent vector store.
- `fastapi` and `uvicorn` are in `requirements.txt` but no API layer exists yet; the project runs as a plain script.
- OCR corrections and known-skill casing are hardcoded in `extract_skills()` — extend those dicts when adding support for new skills or fixing misreads.
