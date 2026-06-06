"""
app/logger.py — AI Career Copilot
Centralised logging configuration.

Creates a rotating log file at  <project_root>/logs/copilot.log  (max 5 MB,
3 backups kept) so users can attach the file when reporting bugs.

Usage (in every module):
    from .logger import get_logger
    log = get_logger(__name__)
    log.info("...")
    log.debug("...")
    log.warning("...")
    log.error("exc msg", exc_info=True)   # includes full traceback

Levels:
    DEBUG   — intermediate values, chunk counts, similarity scores, etc.
    INFO    — pipeline stage milestones (mirrors existing print statements)
    WARNING — recoverable issues (OCR fallback, sparse text, missing poppler)
    ERROR   — exceptions; always with exc_info=True so tracebacks land in the log
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "logs")
_LOG_FILE = os.path.join(_LOG_DIR, "copilot.log")
_MAX_BYTES = 5 * 1024 * 1024   # 5 MB per file
_BACKUP_COUNT = 3               # keep copilot.log, copilot.log.1, .2, .3

_FMT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
_DATE_FMT = "%Y-%m-%d %H:%M:%S"

# ---------------------------------------------------------------------------
# One-time setup (runs when this module is first imported)
# ---------------------------------------------------------------------------

def _setup_root_logger() -> None:
    """Configure the root logger once per process."""
    root = logging.getLogger("app")
    if root.handlers:
        return  # already configured — skip

    root.setLevel(logging.DEBUG)

    # ── File handler (always DEBUG so every detail lands in the log) ──────
    os.makedirs(_LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(
        _LOG_FILE,
        maxBytes=_MAX_BYTES,
        backupCount=_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(_FMT, datefmt=_DATE_FMT))
    root.addHandler(file_handler)

    # ── Console handler (WARNING+ only — don't clutter the CLI output) ───
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(logging.WARNING)
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    root.addHandler(console_handler)

    # ── Log uncaught exceptions so crash traces end up in the file ────────
    def _log_uncaught(exc_type, exc_value, exc_tb):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_tb)
            return
        root.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_tb))
    sys.excepthook = _log_uncaught


_setup_root_logger()


# ---------------------------------------------------------------------------
# Public helper
# ---------------------------------------------------------------------------

def get_logger(name: str) -> logging.Logger:
    """
    Return a child logger under the 'app' namespace.

    Args:
        name: Typically __name__ from the calling module.
              e.g. 'app.rag_pipeline' → child of the 'app' root logger.

    Returns:
        A Logger instance that writes to logs/copilot.log automatically.
    """
    return logging.getLogger(name)


def log_file_path() -> str:
    """Return the absolute path of the current log file."""
    return os.path.abspath(_LOG_FILE)
