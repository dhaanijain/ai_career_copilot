import sys
import os

# Ensure project root is on path so `app.*` imports resolve from any CWD
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from backend_api.routes import resume, jd_match, recommendations, skill_gap

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")

# Allow extra origins via comma-separated ALLOWED_ORIGINS env var
_extra_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", "").split(",")
    if o.strip()
]
CORS_ORIGINS = ["http://localhost:3000", "http://127.0.0.1:3000"] + _extra_origins


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    yield


app = FastAPI(
    title="AI Career Copilot API",
    description=(
        "Backend API for AI-powered career analysis and job matching.\n\n"
        "All endpoints are versioned under `/api/v1`. "
        "Authentication is optional — pass a Supabase JWT `Bearer` token "
        "to have results persisted to your account."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Structured error handler ──────────────────────────────────────────────────
@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_ERROR",
            "detail": "An unexpected error occurred. Please try again.",
        },
    )


# ── Versioned routes ──────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(resume.router, prefix=API_PREFIX, tags=["Resume"])
app.include_router(jd_match.router, prefix=API_PREFIX, tags=["JD Match"])
app.include_router(recommendations.router, prefix=API_PREFIX, tags=["Recommendations"])
app.include_router(skill_gap.router, prefix=API_PREFIX, tags=["Skill Gap"])


@app.get("/health", tags=["Health"])
def health():
    return {"status": "ok", "version": "1.0.0"}
