"""
app/utils.py — AI Career Copilot
Shared utility functions used across all modules.
"""

import re
from typing import List


def normalize_skill_name(skill: str) -> str:
    """Lowercase and collapse whitespace for canonical skill comparison."""
    return re.sub(r"\s+", " ", skill.lower().strip())


def deduplicate_ordered(items: List[str]) -> List[str]:
    """Remove case-insensitive duplicates while preserving insertion order."""
    seen: set = set()
    out: List[str] = []
    for item in items:
        key = normalize_skill_name(item)
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out


def pct_str(value: float, decimals: int = 1) -> str:
    """Format a 0–1 float as a percentage string. e.g. 0.823 → '82.3%'"""
    return f"{value * 100:.{decimals}f}%"
