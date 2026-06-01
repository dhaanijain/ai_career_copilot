"""
app/retrieval_engine.py — AI Career Copilot
FAISS-based retrieval pipeline for plain text (no PDF involved).

Reuses rag_pipeline's chunk/embed/index/retrieve primitives so the
SentenceTransformer model is loaded once per process via the singleton.
Use this when you have a long text document and want to surface only
the most skill-relevant regions before running extraction.
"""

from typing import List, Tuple

import faiss
import numpy as np

from .rag_pipeline import (
    RETRIEVAL_QUERIES,
    build_index,
    chunk_text,
    embed,
    retrieve_chunks,
)


def build_text_index(
    text: str,
    chunk_size: int = 400,
    overlap: int = 80,
) -> Tuple[List[str], np.ndarray, faiss.IndexFlatIP]:
    """
    Chunk, embed, and index raw text in a single call.
    Returns (chunks, embeddings, index) ready for retrieval.
    """
    chunks = chunk_text(text, chunk_size=chunk_size, overlap=overlap)
    embeddings = embed(chunks)
    index = build_index(embeddings)
    return chunks, embeddings, index


def retrieve_from_text(
    text: str,
    queries: List[str] = RETRIEVAL_QUERIES,
    top_k: int = 10,
) -> List[str]:
    """
    Full retrieval pipeline for plain text: chunk → embed → index → retrieve.

    Useful for longer documents (e.g. multi-page text resumes, company wikis)
    where you want semantic focus before extraction reduces noise.
    """
    chunks, embeddings, index = build_text_index(text)
    return retrieve_chunks(queries, index, chunks, embeddings, top_k=top_k)
