import sys
import os

# Ensure project root is on path so `app.*` imports resolve from any CWD
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from backend_api.routes import resume, jd_match, recommendations, skill_gap

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    yield


app = FastAPI(
    title="AI Career Copilot API",
    description="Backend API for AI-powered career analysis and job matching",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router, tags=["Resume"])
app.include_router(jd_match.router, tags=["JD Match"])
app.include_router(recommendations.router, tags=["Recommendations"])
app.include_router(skill_gap.router, tags=["Skill Gap"])


@app.get("/health")
def health():
    return {"status": "ok"}
