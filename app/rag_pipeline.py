"""
app/rag_pipeline.py — AI Career Copilot
Redesigned for robust, generalizable technical skill extraction.

Pipeline stages:
  1  Load      — pdfplumber text extraction + OCR fallback at 300 DPI
  2  OCR Fix   — correct common OCR misreads before any downstream logic
  3  Clean     — strip PII noise (emails, URLs, phones); normalize whitespace
  4  Sections  — isolate skill-bearing regions; full doc used as fallback
  5  Chunk     — deduplicated chunks via content hashing
  6  Embed     — L2-normalized sentence embeddings → cosine similarity space
  7  Index     — FAISS inner-product index (IP on unit vectors = cosine)
  8  Retrieve  — multi-query retrieval with diversity-based deduplication
  9  Extract   — whitelist-first + section heuristics + confidence scoring
"""

import os
import platform
import re
import hashlib
import sys
import pdfplumber
import pytesseract
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import Dict, List, NoReturn, Optional, Set, Tuple

try:
    from .logger import get_logger  # works when imported as a package module
except ImportError:
    from app.logger import get_logger  # fallback for direct-script invocation

log = get_logger(__name__)

# import pandas as pd


# =============================================================================
# CONFIGURATION — extend these dicts/sets; logic below never needs touching
# =============================================================================

# Every key is a lowercase variant or OCR misread; value is the display form.
# Multi-word entries are matched with a sliding window, so "machine learning"
# is found even inside "Python machine learning frameworks".
SKILL_TAXONOMY: Dict[str, str] = {
    # ── Programming Languages ──────────────────────────────────────────────
    "python": "Python",         "java": "Java",
    "javascript": "JavaScript", "typescript": "TypeScript",
    "c": "C",                   "c++": "C++",               "c#": "C#",
    "go": "Go",                 "golang": "Go",
    "rust": "Rust",             "ruby": "Ruby",             "php": "PHP",
    "swift": "Swift",           "kotlin": "Kotlin",         "scala": "Scala",
    "r": "R",                   "matlab": "MATLAB",         "julia": "Julia",
    "perl": "Perl",             "dart": "Dart",             "lua": "Lua",
    "haskell": "Haskell",       "elixir": "Elixir",
    "groovy": "Groovy",         "bash": "Bash",             "shell": "Shell",
    "powershell": "PowerShell", "assembly": "Assembly",
    "solidity": "Solidity",     "verilog": "Verilog",

    # ── Web & Frontend ─────────────────────────────────────────────────────
    "react": "React",           "reactjs": "React",         "react.js": "React",
    "angular": "Angular",       "angularjs": "Angular",
    "vue": "Vue.js",            "vuejs": "Vue.js",          "vue.js": "Vue.js",
    "svelte": "Svelte",
    "next.js": "Next.js",       "nextjs": "Next.js",
    "nuxt": "Nuxt.js",          "nuxt.js": "Nuxt.js",
    "gatsby": "Gatsby",
    "html": "HTML",             "html5": "HTML5",
    "css": "CSS",               "css3": "CSS3",
    "sass": "Sass",             "less": "Less",
    "bootstrap": "Bootstrap",
    "tailwind": "Tailwind CSS", "tailwindcss": "Tailwind CSS",
    "jquery": "jQuery",
    "webpack": "Webpack",       "vite": "Vite",             "babel": "Babel",
    "redux": "Redux",           "graphql": "GraphQL",
    "rest": "REST",             "restful": "REST",

    # ── Backend Frameworks ─────────────────────────────────────────────────
    "node.js": "Node.js",       "nodejs": "Node.js",
    "express": "Express.js",    "express.js": "Express.js",
    "fastapi": "FastAPI",       "flask": "Flask",           "django": "Django",
    "spring": "Spring",         "spring boot": "Spring Boot",
    "rails": "Ruby on Rails",   "laravel": "Laravel",
    "asp.net": "ASP.NET",       ".net": ".NET",             "dotnet": ".NET",

    # ── Data Science / ML / AI ─────────────────────────────────────────────
    "tensorflow": "TensorFlow", "pytorch": "PyTorch",
    "keras": "Keras",
    "scikit-learn": "Scikit-learn", "sklearn": "Scikit-learn",
    "scikit learn": "Scikit-learn",
    "pandas": "Pandas",         "numpy": "NumPy",
    "scipy": "SciPy",           "matplotlib": "Matplotlib",
    "seaborn": "Seaborn",       "plotly": "Plotly",
    "opencv": "OpenCV",
    "nltk": "NLTK",             "spacy": "spaCy",
    "transformers": "Transformers",
    "hugging face": "Hugging Face", "huggingface": "Hugging Face",
    "langchain": "LangChain",
    "openai": "OpenAI",         "anthropic": "Anthropic",
    "llama": "LLaMA",           "llama2": "LLaMA",
    "xgboost": "XGBoost",       "lightgbm": "LightGBM",    "catboost": "CatBoost",
    "faiss": "FAISS",
    "sentence transformers": "Sentence Transformers",
    "word2vec": "Word2Vec",     "bert": "BERT",             "gpt": "GPT",
    "stable diffusion": "Stable Diffusion",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "computer vision": "Computer Vision",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "reinforcement learning": "Reinforcement Learning",

    # ── Databases ──────────────────────────────────────────────────────────
    "sql": "SQL",               "nosql": "NoSQL",
    "mysql": "MySQL",           "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
    "sqlite": "SQLite",         "mongodb": "MongoDB",       "redis": "Redis",
    "elasticsearch": "Elasticsearch", "cassandra": "Cassandra",
    "dynamodb": "DynamoDB",     "firestore": "Firestore",
    "neo4j": "Neo4j",           "influxdb": "InfluxDB",
    "clickhouse": "ClickHouse", "snowflake": "Snowflake",
    "bigquery": "BigQuery",     "redshift": "Redshift",
    "oracle": "Oracle",         "sql server": "SQL Server", "mssql": "SQL Server",

    # ── Cloud Platforms ────────────────────────────────────────────────────
    "aws": "AWS",               "amazon web services": "AWS",
    "azure": "Azure",           "microsoft azure": "Azure",
    "gcp": "GCP",               "google cloud": "GCP",
    "google cloud platform": "GCP",
    "heroku": "Heroku",         "vercel": "Vercel",
    "netlify": "Netlify",       "digitalocean": "DigitalOcean",
    "cloudflare": "Cloudflare", "firebase": "Firebase",
    "lambda": "AWS Lambda",     "ec2": "AWS EC2",
    "s3": "AWS S3",             "sagemaker": "SageMaker",

    # ── DevOps & Infrastructure ────────────────────────────────────────────
    "docker": "Docker",         "kubernetes": "Kubernetes", "k8s": "Kubernetes",
    "jenkins": "Jenkins",
    "github actions": "GitHub Actions",
    "gitlab ci": "GitLab CI",   "travis ci": "Travis CI",
    "circleci": "CircleCI",     "ansible": "Ansible",
    "terraform": "Terraform",   "helm": "Helm",
    "prometheus": "Prometheus", "grafana": "Grafana",
    "nginx": "Nginx",           "apache": "Apache",
    "ci/cd": "CI/CD",           "cicd": "CI/CD",

    # ── Operating Systems ──────────────────────────────────────────────────
    "linux": "Linux",           "ubuntu": "Ubuntu",
    "centos": "CentOS",         "debian": "Debian",
    "windows": "Windows",       "macos": "macOS",

    # ── Developer Tools ────────────────────────────────────────────────────
    "git": "Git",               "github": "GitHub",
    "gitlab": "GitLab",         "bitbucket": "Bitbucket",
    "jira": "Jira",             "confluence": "Confluence",
    "figma": "Figma",           "postman": "Postman",
    "swagger": "Swagger",       "jupyter": "Jupyter",
    "google colab": "Google Colab", "colab": "Google Colab",
    "vscode": "VS Code",        "vs code": "VS Code",
    "intellij": "IntelliJ",     "pycharm": "PyCharm",
    "android studio": "Android Studio",

    # ── Mobile ────────────────────────────────────────────────────────────
    "android": "Android",       "ios": "iOS",
    "react native": "React Native", "flutter": "Flutter",

    # ── Concepts & Paradigms ──────────────────────────────────────────────
    "oop": "OOP",               "mvc": "MVC",
    "microservices": "Microservices",
    "agile": "Agile",           "scrum": "Scrum",
    "data structures": "Data Structures",
    "algorithms": "Algorithms",
    "object oriented programming": "OOP",
    "object-oriented programming": "OOP",
    "api": "API",               "apis": "API",
}

# OCR misread → correct lowercase form.
# Applied to the full raw text before anything else.
# Longer phrases must come first so they match before their substrings do.
OCR_CORRECTIONS: Dict[str, str] = {
    # AI / ML
    "openal": "openai",         "open al": "openai",    "open a i": "openai",
    "tensor flow": "tensorflow","tensorfow": "tensorflow","tensorfiow": "tensorflow",
    "py torch": "pytorch",      "py-torch": "pytorch",
    "scikit learn": "scikit-learn", "sci-kit learn": "scikit-learn",
    "scikitlearn": "scikit-learn",
    "hugging face": "hugging face",  # keep — already correct, just normalizes
    # Web
    "node js": "node.js",       "node-js": "node.js",
    "react js": "react",        "react-js": "react",
    "angular js": "angular",    "angular-js": "angular",
    "vue js": "vue.js",         "vue-js": "vue.js",
    "next js": "next.js",       "next-js": "next.js",
    "express js": "express.js",
    "tail wind": "tailwind",    "tail-wind": "tailwind",
    # Version control / DevOps
    "git hub": "github",        "git-hub": "github",
    "kub ernetes": "kubernetes","kubernates": "kubernetes",
    "kubernetis": "kubernetes",
    # Databases
    "mongo db": "mongodb",      "mongo-db": "mongodb",
    "postgre sql": "postgresql","postgre-sql": "postgresql",
    "my sql": "mysql",          "my-sql": "mysql",
    # Languages
    "java script": "javascript","java-script": "javascript",
    "type script": "typescript","type-script": "typescript",
    "pythor": "python",         "pythom": "python",
    "javascrpt": "javascript",
    "c + +": "c++",
    # Tools
    "power shell": "powershell","power-shell": "powershell",
}

# Regex patterns that immediately disqualify a token as a skill candidate
_NON_SKILL_PATTERNS: List[str] = [
    r"^\d+(?:\.\d+)?$",                              # pure number / GPA (e.g. 8.89)
    r"^\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4}$",         # date formats
    r"\b(?:19|20)\d{2}\b",                            # 4-digit year
    r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}",     # email address
    r"https?://\S+",                                  # URL (http/https)
    r"www\.[a-z0-9\-]+\.[a-z]{2,}",                  # URL (www.xxx)
    r"\+?\d[\d\s\-\(\)]{7,}\d",                      # phone number
]
_NON_SKILL_RE = re.compile("|".join(_NON_SKILL_PATTERNS), re.IGNORECASE)

# Single tokens that represent resume boilerplate, not skills.
# Checked after lowercasing.
NON_SKILL_WORDS: Set[str] = {
    # Section headings
    "education", "experience", "contact", "objective", "summary",
    "profile", "projects", "project", "achievements", "achievement",
    "certifications", "certification", "awards", "award", "references",
    "reference", "skills", "technologies", "tools", "languages",
    "frameworks", "competencies", "proficiency",
    # Institutions / places
    "university", "college", "school", "institute", "organization",
    "company", "location", "address",
    # PII-adjacent
    "phone", "email", "linkedin", "portfolio", "website", "resume", "cv",
    # Academic noise
    "grade", "percentage", "cgpa", "gpa", "semester", "batch",
    "honours", "honors", "distinction",
    # Job-role words (not skills)
    "name", "date", "month", "year", "work", "internship",
    "position", "role", "intern", "engineer", "developer", "manager",
    # Soft skills / filler
    "team", "communication", "collaboration", "management", "leadership",
    "problem", "solving", "analytical", "creative", "passionate",
    "enthusiastic", "excellent", "strong", "experienced", "motivated",
    "knowledge", "understanding", "proficient", "familiar", "exposure",
    "ability", "good", "best", "various", "multiple", "several",
    # Common English words that slip through
    "the", "and", "or", "for", "with", "from", "into", "that", "this",
    "have", "has", "been", "using", "used", "use", "able", "well",
    "also", "such", "both", "between", "including", "include",
    # OCR / formatting noise
    "page", "section", "list", "item", "table", "figure", "me",
}

# Regex alternates used by _SKILL_HEADING_RE to detect skill-section headings.
SKILL_SECTION_PATTERNS: List[str] = [
    r"technical\s+skills?",
    r"skills?",
    r"technologies",
    r"tools?\s+(?:&|and)?\s*technologies",
    r"core\s+competencies",
    r"competencies",
    r"tech(?:nical)?\s+stack",
    r"programming\s+languages?",
    r"languages?\s+(?:&|and)?\s*(?:tools?|frameworks?)",
    r"frameworks?\s+(?:&|and)?\s+libraries",
    r"libraries?\s+(?:&|and)?\s+frameworks?",
    r"software\s+skills?",
    r"technical\s+proficiency",
    r"proficiencies",
    r"areas?\s+of\s+expertise",
    r"expertise",
]

# Multiple targeted queries give better FAISS coverage than a single broad one
RETRIEVAL_QUERIES: List[str] = [
    "technical skills programming languages frameworks libraries",
    "cloud platforms databases infrastructure DevOps tools",
    "machine learning deep learning AI NLP data science libraries",
    "frontend backend web development technologies stack",
    "developer tools version control CI/CD pipelines",
]


# =============================================================================
# STAGE 1 — DOCUMENT LOADING
# =============================================================================

# Common Windows install locations for Poppler, checked in priority order.
_WINDOWS_POPPLER_CANDIDATES: List[str] = [
    r"C:\Program Files\poppler\bin",
    r"C:\Program Files (x86)\poppler\bin",
    r"C:\poppler\bin",
    r"C:\tools\poppler\bin",
    # project-local vendor bundle (checked relative to this file)
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vendor", "poppler", "bin"),
]


def _find_poppler_path() -> Optional[str]:
    """
    Locate the Poppler bin directory so convert_from_path works on Windows.

    Resolution order:
      1. POPPLER_PATH environment variable (set this in .env or shell)
      2. Common Windows install locations
      3. Return None → let pdf2image use the system PATH (correct for macOS/Linux)
    """
    # Always respect an explicit override first
    env_path = os.environ.get("POPPLER_PATH")
    if env_path:
        pdftoppm = os.path.join(env_path, "pdftoppm.exe" if platform.system() == "Windows" else "pdftoppm")
        if os.path.isfile(pdftoppm):
            return env_path
        log.warning("POPPLER_PATH is set to '%s' but pdftoppm was not found there.", env_path)
        print(f"  ⚠  POPPLER_PATH is set to '{env_path}' but pdftoppm was not found there.")

    if platform.system() != "Windows":
        # macOS / Linux: Poppler is on the system PATH after `brew install poppler`
        # or `apt install poppler-utils` — no path override needed.
        return None

    for candidate in _WINDOWS_POPPLER_CANDIDATES:
        if os.path.isfile(os.path.join(candidate, "pdftoppm.exe")):
            return candidate

    return None


def _ocr_fallback(path: str) -> str:
    """
    Convert PDF pages to images via pdf2image and run pytesseract OCR.
    Raises RuntimeError with actionable instructions when Poppler is missing.
    """
    try:
        from pdf2image import convert_from_path  # type: ignore[import-untyped]
        from pdf2image.exceptions import PDFInfoNotInstalledError  # type: ignore[import-untyped]
    except ImportError as exc:
        raise RuntimeError(
            "pdf2image is not installed. Run: pip install pdf2image"
        ) from exc

    poppler_path = _find_poppler_path()
    images: list = []  # always bound before the loop below

    try:
        if poppler_path:
            images = convert_from_path(path, dpi=300, poppler_path=poppler_path)
        else:
            images = convert_from_path(path, dpi=300)
    except PDFInfoNotInstalledError:  # type: ignore[possibly-unbound]
        _raise_poppler_missing_error(poppler_path)
    except Exception as exc:
        log.error("pdf2image conversion failed for '%s': %s", path, exc, exc_info=True)
        raise RuntimeError(f"pdf2image conversion failed: {exc}") from exc

    text = ""
    for img in images:
        text += pytesseract.image_to_string(img) + "\n"
    return text


def _raise_poppler_missing_error(attempted_path: Optional[str]) -> NoReturn:
    path_hint = f"  Tried path: {attempted_path}\n" if attempted_path else ""
    raise RuntimeError(
        "\n"
        "╔══════════════════════════════════════════════════════════════╗\n"
        "║  Poppler is not installed or not on PATH.                    ║\n"
        "║  pdf2image requires Poppler's pdftoppm binary.               ║\n"
        "╠══════════════════════════════════════════════════════════════╣\n"
        "║  WINDOWS FIX                                                 ║\n"
        "║  1. Download from:                                           ║\n"
        "║     https://github.com/oschwartz10612/poppler-windows/releases║\n"
        "║  2. Extract to: C:\\Program Files\\poppler\\                   ║\n"
        "║  3. Add to PATH: C:\\Program Files\\poppler\\bin               ║\n"
        "║     (Win+S → 'Edit system environment variables' → Path)     ║\n"
        "║  4. Restart your terminal, then re-run.                      ║\n"
        "║                                                              ║\n"
        "║  OR: Set env var (no PATH change needed):                    ║\n"
        "║     $env:POPPLER_PATH = 'C:\\Program Files\\poppler\\bin'     ║\n"
        "║                                                              ║\n"
        "║  macOS FIX:   brew install poppler                           ║\n"
        "║  Linux FIX:   sudo apt install poppler-utils                 ║\n"
        "╠══════════════════════════════════════════════════════════════╣\n"
        "║  SKIP OCR (pdfplumber text only): set env var                ║\n"
        "║     $env:SKIP_OCR = '1'                                      ║\n"
        "╚══════════════════════════════════════════════════════════════╝\n"
        + path_hint
    )


def load_pdf(path: str) -> str:
    """
    Extract text from a PDF resume.

    Primary:  pdfplumber (fast, no external deps).
    Fallback: pdf2image + pytesseract OCR at 300 DPI when text layer is sparse
              (scanned PDFs, image-only PDFs).

    Set SKIP_OCR=1 to disable the OCR fallback entirely (useful in CI or when
    Poppler is unavailable and the PDF has a readable text layer).
    """
    text = ""
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

    if len(text.strip()) >= 100:
        log.info("PDF text layer OK: %d chars extracted from '%s'", len(text), path)
        return text

    # Text layer is sparse — attempt OCR
    if os.environ.get("SKIP_OCR", "").strip() == "1":
        log.warning("Sparse text layer in '%s' but SKIP_OCR=1 — returning partial text (%d chars)", path, len(text))
        print("  ⚠  sparse text layer but SKIP_OCR=1 — returning partial text")
        return text

    log.warning("Sparse text layer in '%s' (%d chars) — engaging OCR at 300 DPI", path, len(text))
    print("  ⚠  sparse text layer — engaging OCR at 300 DPI")
    try:
        text += _ocr_fallback(path)
        log.info("OCR completed for '%s': total %d chars", path, len(text))
    except RuntimeError as exc:
        # Surface the full message so the user sees exactly what to do
        log.error("OCR failed for '%s': %s", path, exc, exc_info=True)
        print(str(exc))
        print("  ⚠  OCR failed — returning partial text from pdfplumber")

    return text


# =============================================================================
# STAGE 2 — OCR NORMALIZATION (runs before any text cleaning or analysis)
# =============================================================================

def normalize_ocr(text: str) -> str:
    """
    Replace known OCR misreads in the raw document text.
    Case-insensitive so it catches 'Tensor Flow', 'tensor flow', 'TENSOR FLOW'.
    Replacements are lowercase to avoid casing ambiguity; canonical casing is
    restored later from SKILL_TAXONOMY during extraction.
    Longer entries in OCR_CORRECTIONS are applied first (sorted by length desc)
    so 'tensor flow' is caught before 'tensorflow' would shadow it.
    """
    for wrong, correct in sorted(OCR_CORRECTIONS.items(), key=lambda x: -len(x[0])):
        text = re.sub(re.escape(wrong), correct, text, flags=re.IGNORECASE)
    return text


# =============================================================================
# STAGE 3 — TEXT CLEANING
# =============================================================================

def clean_text(text: str) -> str:
    """
    Remove PII and noise while preserving structural newlines.
    Newlines are preserved because section detection (stage 4) uses them
    to find headings.
    """
    text = re.sub(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\+?\d[\d\s\-\(\)]{7,}\d", " ", text)
    # Keep alphanumeric + characters used in skill names (. - + # / &)
    text = re.sub(r"[^a-zA-Z0-9\s.\-+#/&]", " ", text)
    text = re.sub(r"[^\S\n]+", " ", text)   # collapse horizontal whitespace
    text = re.sub(r"\n{3,}", "\n\n", text)  # max 2 consecutive blank lines
    return text.strip()


# =============================================================================
# STAGE 4 — SKILL SECTION DETECTION
# =============================================================================

_SKILL_HEADING_RE = re.compile(
    r"^\s*(?:" + "|".join(SKILL_SECTION_PATTERNS) + r")\s*[:\-]?\s*$",
    re.IGNORECASE,
)
# Heuristic for detecting that we've entered a new (non-skill) section:
# a short line (≤ 5 words) that looks like a heading.
_GENERIC_HEADING_RE = re.compile(r"^[A-Z][A-Za-z\s&/\-]{2,40}$")


def extract_skill_sections(text: str) -> Tuple[str, str]:
    """
    Scan the document line by line and pull out skill-bearing sections.
    Returns (skill_section_text, full_text).
    skill_section_text is used as the high-confidence source for extraction.
    full_text is retained as the FAISS corpus so we don't lose any context.
    Falls back to full_text when no skill section is detected.
    """
    lines = text.split("\n")
    skill_lines: List[str] = []
    in_skill_section = False

    for line in lines:
        stripped = line.strip()

        if not stripped:
            if in_skill_section:
                skill_lines.append("")
            continue

        if _SKILL_HEADING_RE.match(stripped):
            in_skill_section = True
            skill_lines.append(stripped)
            continue

        if in_skill_section:
            word_count = len(stripped.split())
            # A short capitalised line after we've collected some content
            # signals the start of a new section → stop collecting.
            if (
                word_count <= 4
                and _GENERIC_HEADING_RE.match(stripped)
                and len(skill_lines) > 3
            ):
                in_skill_section = False
            else:
                skill_lines.append(stripped)

    skill_text = "\n".join(skill_lines).strip()
    return (skill_text if len(skill_text) >= 20 else text), text


# =============================================================================
# STAGE 5 — CHUNKING WITH DEDUPLICATION
# =============================================================================

def chunk_text(text: str, chunk_size: int = 400, overlap: int = 80) -> List[str]:
    """
    Split text and drop near-duplicate chunks via MD5 of normalised content.
    Smaller chunks (400 vs old 500) keep retrieved context tighter.
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", " ", ""],
    )
    seen: Set[str] = set()
    unique: List[str] = []
    for chunk in splitter.split_text(text):
        key = hashlib.md5(re.sub(r"\s+", " ", chunk.lower().strip()).encode()).hexdigest()
        if key not in seen:
            seen.add(key)
            unique.append(chunk)
    return unique


# =============================================================================
# STAGE 6 — EMBEDDINGS (cosine similarity via L2 normalisation)
# =============================================================================

_MODEL: Optional[SentenceTransformer] = None


def _get_model() -> SentenceTransformer:
    """Singleton — load once per process to avoid repeated disk I/O."""
    global _MODEL
    if _MODEL is None:
        _MODEL = SentenceTransformer("all-MiniLM-L6-v2")
    return _MODEL


def embed(texts: List[str]) -> np.ndarray:
    """
    Encode texts and L2-normalise so that inner product == cosine similarity.
    This lets us use faiss.IndexFlatIP (fast exact search) as a cosine index.
    L2 distance on un-normalised vectors is biased by embedding magnitude;
    cosine is purely directional — the right metric for semantic similarity.
    """
    vecs = np.array(_get_model().encode(texts, show_progress_bar=False), dtype="float32")
    faiss.normalize_L2(vecs)
    return vecs


def build_index(embeddings: np.ndarray) -> faiss.IndexFlatIP:
    """Inner-product index on unit-normalised vectors = cosine search."""
    idx = faiss.IndexFlatIP(embeddings.shape[1])
    idx.add(embeddings.astype("float32"))  # type: ignore[call-arg]  # faiss stubs don't expose the Python-friendly overload
    return idx


# =============================================================================
# STAGE 7 — MULTI-QUERY RETRIEVAL WITH DIVERSITY FILTERING
# =============================================================================

def retrieve_chunks(
    queries: List[str],
    index: faiss.IndexFlatIP,
    chunks: List[str],
    embeddings: np.ndarray,
    top_k: int = 10,
    diversity_threshold: float = 0.88,
) -> List[str]:
    """
    Retrieve semantically relevant chunks across multiple queries, then
    drop near-duplicates using a greedy diversity filter (MMR-style).

    Multi-query strategy: different queries surface different skill domains
    (e.g. 'cloud platforms' vs 'ML libraries') so we don't miss sections
    that a single generic query would rank low.

    diversity_threshold: cosine similarity above which a second chunk is
    considered redundant and discarded (keeps retrieved set non-repetitive).
    """
    model = _get_model()
    best_score: Dict[int, float] = {}

    for query in queries:
        q_vec = np.array(model.encode([query]), dtype="float32")
        faiss.normalize_L2(q_vec)
        k = min(top_k * 2, len(chunks))
        scores, indices = index.search(q_vec, k)  # type: ignore[call-arg]
        for score, idx in zip(scores[0], indices[0]):
            if idx >= 0:
                best_score[idx] = max(best_score.get(idx, 0.0), float(score))

    ranked = sorted(best_score.items(), key=lambda x: -x[1])

    selected: List[str] = []
    selected_vecs: List[np.ndarray] = []

    for chunk_idx, _ in ranked:
        if len(selected) >= top_k:
            break
        vec = embeddings[chunk_idx]
        if any(float(np.dot(vec, sv)) >= diversity_threshold for sv in selected_vecs):
            continue
        selected_vecs.append(vec)
        selected.append(chunks[chunk_idx])

    return selected


# =============================================================================
# STAGE 8 — SKILL EXTRACTION
# =============================================================================

def _is_garbage(token: str) -> bool:
    """True when a token is definitely not a skill (PII, number, date, URL)."""
    return bool(_NON_SKILL_RE.search(token.lower()))


def _confidence(canonical: str, from_skill_section: bool) -> float:
    """
    Three-tier confidence scale:
      1.0 — in whitelist AND from a detected skill section
      0.8 — in whitelist, found elsewhere in the document
      0.5 — not in whitelist but in a skill section, looks technical
      0.0 — everything else
    """
    in_wl = canonical.lower() in SKILL_TAXONOMY or canonical in SKILL_TAXONOMY.values()
    if in_wl:
        return 1.0 if from_skill_section else 0.8
    if from_skill_section:
        words = canonical.split()
        if (
            1 <= len(words) <= 3
            and len(canonical) <= 30
            and re.search(r"[A-Z0-9]", canonical)          # looks like a proper noun / acronym
            and not any(w.lower() in NON_SKILL_WORDS for w in words)
        ):
            return 0.5
    return 0.0


def extract_technical_skills(
    retrieved_chunks: List[str],
    skill_section_text: str = "",
    confidence_threshold: float = 0.5,
) -> List[Dict]:
    """
    Whitelist-first skill extraction with per-skill confidence scoring.

    Strategy:
    1. Process skill-section text first (high confidence).
    2. Process FAISS-retrieved chunks (medium confidence).
    3. For each text fragment, split on common list delimiters then apply
       a sliding n-gram window (n = 3 → 2 → 1) to find the longest
       whitelist match.  This catches 'machine learning' inside
       'Python machine learning frameworks' without ever hardcoding positions.
    4. Unknown tokens from skill sections pass if they look technical
       (uppercase/digit present, 1-3 words, not boilerplate).

    Returns list of {"skill": str, "confidence": float} sorted by confidence
    desc then alphabetically — ready to be consumed by downstream JD matching.
    """
    results: Dict[str, float] = {}  # canonical_name → best confidence seen

    # Pre-sort corrections by length so longer phrases match first
    _sorted_corrections = sorted(OCR_CORRECTIONS.items(), key=lambda x: -len(x[0]))

    def _process(text: str, from_skill_section: bool) -> None:
        # Strip any residual PII before tokenising
        text = re.sub(r"[a-z0-9._%+\-]+@[a-z0-9.\-]+\.[a-z]{2,}", "", text, flags=re.I)
        text = re.sub(r"https?://\S+|www\.\S+", "", text, flags=re.I)

        # Split on characters that separate items in skill lists
        parts = re.split(r"[,|•·\n/]", text)

        for part in parts:
            part = part.strip(" \t-–—")
            if len(part) < 2:
                continue

            # Belt-and-suspenders OCR correction at extraction time
            part_lower = part.lower()
            for wrong, correct in _sorted_corrections:
                part_lower = part_lower.replace(wrong, correct)

            # Fast-reject: entire part is PII / number / date
            if _is_garbage(part_lower):
                continue

            tokens = part_lower.split()
            if not tokens:
                continue

            found_any_whitelist_match = False

            # Sliding window: longest match wins to avoid partial overlaps
            for n in (3, 2, 1):
                for start in range(len(tokens) - n + 1):
                    candidate_lower = " ".join(tokens[start : start + n])

                    # Skip pure-numeric / date / boilerplate tokens
                    if _is_garbage(candidate_lower):
                        continue
                    if n == 1 and candidate_lower in NON_SKILL_WORDS:
                        continue

                    if candidate_lower in SKILL_TAXONOMY:
                        canonical = SKILL_TAXONOMY[candidate_lower]
                        score = _confidence(canonical, from_skill_section)
                        if score >= confidence_threshold:
                            results[canonical] = max(results.get(canonical, 0.0), score)
                        found_any_whitelist_match = True

            # Unknown-token heuristic: only for skill sections, short parts
            # that contain uppercase/digits (look like proper tech names).
            if not found_any_whitelist_match and from_skill_section:
                orig_words = part.split()
                if 1 <= len(orig_words) <= 3:
                    candidate_orig = " ".join(orig_words)
                    score = _confidence(candidate_orig, from_skill_section=True)
                    if score >= confidence_threshold:
                        # Preserve casing if mixed, otherwise title-case
                        display = candidate_orig if re.search(r"[A-Z]", candidate_orig) \
                                  else candidate_orig.title()
                        results[display] = max(results.get(display, 0.0), score)

    # High-confidence source first
    if skill_section_text.strip():
        for chunk in chunk_text(skill_section_text, chunk_size=300, overlap=40):
            _process(chunk, from_skill_section=True)

    # FAISS-retrieved chunks
    for chunk in retrieved_chunks:
        _process(chunk, from_skill_section=False)

    output = [
        {"skill": skill, "confidence": round(conf, 2)}
        for skill, conf in results.items()
        if conf >= confidence_threshold
    ]
    output.sort(key=lambda x: (-x["confidence"], x["skill"]))
    return output


# =============================================================================
# MAIN PIPELINE
# =============================================================================

def run_pipeline(resume_path: str, confidence_threshold: float = 0.5) -> List[str]:
    """
    Orchestrates all nine stages. Returns a flat list of skill strings.
    confidence_threshold: raise to 0.8 for stricter (whitelist-only) output;
    lower to 0.4 to surface more unknowns from skill sections.
    """
    log.info("=== run_pipeline START: resume='%s', confidence_threshold=%.2f ===", resume_path, confidence_threshold)
    print(f"\n{'─'*50}")
    print(f"  AI Career Copilot — Resume Skill Extraction")
    print(f"{'─'*50}\n")

    print("📂  [1/7] Loading PDF...")
    log.info("[1/7] Loading PDF: %s", resume_path)
    raw_text = load_pdf(resume_path)
    log.info("[1/7] PDF loaded: %d chars", len(raw_text))
    print(f"      {len(raw_text)} characters extracted")

    print("🔧  [2/7] Normalising OCR artefacts...")
    log.info("[2/7] Normalising OCR artefacts")
    raw_text = normalize_ocr(raw_text)

    print("🧹  [3/7] Cleaning text...")
    log.info("[3/7] Cleaning text")
    clean = clean_text(raw_text)
    log.debug("[3/7] Clean text length: %d chars", len(clean))

    print("🗂   [4/7] Detecting skill sections...")
    log.info("[4/7] Detecting skill sections")
    skill_section_text, full_text = extract_skill_sections(clean)
    log.info("[4/7] Skill section: %d chars | full doc: %d chars", len(skill_section_text), len(full_text))
    print(f"      skill section: {len(skill_section_text)} chars  |  full doc: {len(full_text)} chars")

    print("✂   [5/7] Chunking + deduplication...")
    log.info("[5/7] Chunking and deduplicating")
    chunks = chunk_text(full_text)
    log.info("[5/7] %d unique chunks produced", len(chunks))
    print(f"      {len(chunks)} unique chunks")

    print("🔢  [6/7] Embedding + indexing (cosine)...")
    log.info("[6/7] Embedding %d chunks and building FAISS index", len(chunks))
    embeddings = embed(chunks)
    index = build_index(embeddings)
    log.debug("[6/7] Embedding shape: %s", embeddings.shape)

    print("🔍  [7/7] Multi-query retrieval + skill extraction...")
    log.info("[7/7] Running multi-query retrieval (confidence_threshold=%.2f)", confidence_threshold)
    retrieved = retrieve_chunks(RETRIEVAL_QUERIES, index, chunks, embeddings)
    log.debug("[7/7] Retrieved %d chunks for skill extraction", len(retrieved))
    skill_results = extract_technical_skills(
        retrieved_chunks=retrieved,
        skill_section_text=skill_section_text,
        confidence_threshold=confidence_threshold,
    )

    skills = [item["skill"] for item in skill_results]
    log.info("=== run_pipeline END: %d skills extracted: %s ===", len(skills), skills)
    return skills


# =============================================================================
# ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    from app.logger import log_file_path
    print(f"  Log file → {log_file_path()}")
    log.info("CLI invoked with args: %s", sys.argv)

    path = sys.argv[1] if len(sys.argv) > 1 else "data/Dhaani_Jain_resume.pdf"
    try:
        skills = run_pipeline(path)
    except Exception as _exc:
        log.error("Fatal error during pipeline execution", exc_info=True)
        print(f"\n  ERROR: {_exc}")
        print(f"  Full traceback written to: {log_file_path()}")
        sys.exit(1)

    print(f"\n{'═'*50}")
    print("  EXTRACTED TECHNICAL SKILLS")
    print(f"{'═'*50}")
    for skill in skills:
        print(f"  • {skill}")
    print(f"{'═'*50}")
    print(f"  Total: {len(skills)} skills extracted")
    print(f"{'═'*50}\n")
