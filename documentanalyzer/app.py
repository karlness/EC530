"""
Teacher Document Analyzer – FastAPI backend (clean v1)
======================================================
FastAPI server that connects to **openai-python ≥1.0**.

Endpoints
---------
POST /api/materials  →   Generate lesson plans / quizzes / worksheets.
POST /api/feedback   →   Provide qualitative feedback on a submission.
POST /api/grade      →   Return numeric score + rationale.
"""

# ──────────────────────────────────────────────────────────────────────────────
# Imports & setup
# ──────────────────────────────────────────────────────────────────────────────
import json
import os
import re
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import openai  # v1 client

# Load env vars from .env (if present)
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not set – create a .env file or export the var.")

# Initialise v1 client
client = openai.OpenAI(api_key=OPENAI_API_KEY)
LLM_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", 0.7))

# ──────────────────────────────────────────────────────────────────────────────
# FastAPI app
# ──────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Teacher Document Analyzer API",
    version="1.0.0",
    description="Create classroom material, give feedback, and grade assignments via LLM.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten for production
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────────────────────────────────────
# Pydantic models
# ──────────────────────────────────────────────────────────────────────────────
class MaterialRequest(BaseModel):
    prompt: str
    format: str = "lesson_plan"  # lesson_plan | quiz | worksheet | slides
    length: int = 1               # 1-5 variants

class MaterialResponse(BaseModel):
    materials: List[str]

class FeedbackRequest(BaseModel):
    document: str
    rubric: Optional[str] = None

class FeedbackResponse(BaseModel):
    feedback: str

class GradeRequest(BaseModel):
    answer: str
    rubric: Optional[str] = None
    max_score: int = 100

class GradeResponse(BaseModel):
    score: int
    reasoning: str

# ──────────────────────────────────────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────────────────────────────────────

def ask_llm(prompt: str) -> str:
    """Simple wrapper around the v1 Chat Completions API."""
    try:
        resp = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
        )
        return resp.choices[0].message.content.strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"LLM error: {exc}") from exc

# ──────────────────────────────────────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────────────────────────────────────

@app.post("/api/materials", response_model=MaterialResponse)
async def create_materials(req: MaterialRequest):
    if not (1 <= req.length <= 5):
        raise HTTPException(status_code=400, detail="length must be 1-5")

    prompt = (
        f"You are an experienced educator. Create a {req.format.replace('_',' ')} "
        f"that {req.prompt}. Return the output in markdown format."
    )
    materials = [ask_llm(prompt) for _ in range(req.length)]
    return {"materials": materials}


@app.post("/api/feedback", response_model=FeedbackResponse)
async def give_feedback(req: FeedbackRequest):
    prompt = "Provide constructive, actionable feedback on the following student work.\n\n"
    if req.rubric:
        prompt += f"Rubric:\n{req.rubric}\n\n"
    prompt += f"Student submission:\n{req.document}\n"
    return {"feedback": ask_llm(prompt)}


@app.post("/api/grade", response_model=GradeResponse)
async def grade(req: GradeRequest):
    grading_prompt = (
        f"You are grading on a 0-{req.max_score} scale. Return JSON with keys 'score' and 'reasoning'.\n"
    )
    if req.rubric:
        grading_prompt += f"Rubric:\n{req.rubric}\n"
    grading_prompt += f"Answer:\n{req.answer}\n"

    raw = ask_llm(grading_prompt)
    try:
        parsed = json.loads(raw)
        return GradeResponse(score=int(parsed["score"]), reasoning=parsed["reasoning"])
    except Exception:
        # fallback if model didn't return JSON
        match = re.search(r"(\d+)", raw)
        score = int(match.group(1)) if match else 0
        return GradeResponse(score=score, reasoning=raw)

# ──────────────────────────────────────────────────────────────────────────────
# Root health route (optional)
# ──────────────────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"status": "ok", "version": app.version}
