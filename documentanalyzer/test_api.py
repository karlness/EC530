
"""
Unit-tests for Teacher-Document-Analyzer API
Run with:  pytest -q
"""

import json
import pytest
from fastapi.testclient import TestClient

# import the FastAPI app object
from app import app

# ---------------------------------------------------------------------------
#  Test helpers
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def patch_ask_llm(monkeypatch):
    """
    Monkey-patch app.ask_llm so tests never hit the real OpenAI API.
    The stub decides what to return based on keywords in the prompt.
    """
    def _fake_llm(prompt: str) -> str:
        if "actionable feedback" in prompt:
            return "👍 **Glow:** Clear thesis.\n🔧 **Grow:** Add more evidence."
        if "grading" in prompt or "Return JSON with keys" in prompt:
            return json.dumps({"score": 92, "reasoning": "Correct and well-explained"})
        # default for /materials
        return "### Sample Output\n1. Item one\n2. Item two"

    monkeypatch.setattr("app.ask_llm", _fake_llm)


client = TestClient(app)

# ---------------------------------------------------------------------------
#  /api/materials
# ---------------------------------------------------------------------------

def test_materials_ok():
    payload = {
        "prompt": "teach the water cycle",
        "format": "lesson_plan",
        "length": 2
    }
    r = client.post("/api/materials", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["materials"]                  # list not empty
    assert len(data["materials"]) == 2
    assert data["materials"][0].startswith("###")

def test_materials_bad_length():
    r = client.post("/api/materials", json={
        "prompt": "irrelevant",
        "format": "quiz",
        "length": 10          # > 5 should fail
    })
    assert r.status_code == 400
    assert r.json()["detail"] == "length must be 1-5"

# ---------------------------------------------------------------------------
#  /api/feedback
# ---------------------------------------------------------------------------

def test_feedback_ok():
    r = client.post("/api/feedback", json={
        "document": "My short essay...",
        "rubric": "Clarity 50 | Evidence 50"
    })
    assert r.status_code == 200
    assert "Glow" in r.json()["feedback"]

# ---------------------------------------------------------------------------
#  /api/grade
# ---------------------------------------------------------------------------

def test_grade_json_path():
    r = client.post("/api/grade", json={
        "answer": "Paris is the capital of France.",
        "max_score": 10
    })
    body = r.json()
    assert r.status_code == 200
    assert body["score"] == 92
    assert "reasoning" in body

def test_root_health():
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"