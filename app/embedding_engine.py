"""
app/embedding_engine.py — AI Career Copilot
Semantic embedding utilities for skill-level similarity queries.

Wraps rag_pipeline's embed/index primitives with a skill-focused API.
The SentenceTransformer model is shared via rag_pipeline's singleton,
so it loads once per process regardless of how many modules import this.
"""

from typing import List

import faiss
import numpy as np

from .rag_pipeline import embed


def get_skill_embeddings(skills: List[str]) -> np.ndarray:
    """
    Encode a list of skill names into L2-normalised embeddings.
    Returns shape (n, dim) float32. Empty input returns (0, 384).
    """
    if not skills:
        return np.empty((0, 384), dtype="float32")
    return embed(skills)


def build_skill_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """
    Inner-product index over L2-normalised skill embeddings.
    IP on unit vectors == cosine similarity — no re-normalisation at query time.
    """
    idx = faiss.IndexFlatIP(embeddings.shape[1])
    idx.add(embeddings.astype("float32"))  # type: ignore[call-arg]  # faiss stubs omit the Python-friendly overload
    return idx
