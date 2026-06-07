# tests/engine/test_engine.py

from __future__ import annotations

import json

import src.engine.engine as engine
from src.engine.engine import analyze_job_description


def sample_job_description() -> str:
    return """
    Software Engineering Intern position.

    Responsibilities include building web applications,
    writing tests, and working with a team.

    Requirements include Python, Git, and communication skills.
    """


def sample_gemini_response() -> str:
    return json.dumps(
        {
            "job_title": "Software Engineering Intern",
            "required_skills": ["Python", "Git"],
            "preferred_skills": ["React"],
            "responsibilities": ["Build web applications", "Write tests"],
            "keywords": ["Python", "Git", "teamwork"],
        }
    )


def test_empty_job_description_returns_incomplete():
    result = analyze_job_description("")

    assert result["status"] == "incomplete"
    assert result["message"] == "Job description is required."


def test_invalid_input_returns_invalid_input():
    result = analyze_job_description("I like pizza and movies.")

    assert result["status"] == "invalid_input"
    assert result["message"] == "Input does not appear to be a job description."


def test_analyze_job_description_success(monkeypatch):
    monkeypatch.setattr(
        engine,
        "_call_gemini",
        lambda prompt: sample_gemini_response(),
    )

    result = analyze_job_description(sample_job_description())

    assert result["status"] == "success"
    assert result["data"]["job_title"] == "Software Engineering Intern"
    assert result["data"]["required_skills"] == ["Python", "Git"]
    assert result["data"]["keywords"] == ["Python", "Git", "teamwork"]


def test_gemini_error_returns_ai_error(monkeypatch):
    def fake_call_gemini(prompt: str) -> str:
        raise RuntimeError("API failed")

    monkeypatch.setattr(engine, "_call_gemini", fake_call_gemini)

    result = analyze_job_description(sample_job_description())

    assert result["status"] == "ai_error"
    assert result["message"] == "Could not analyze job description."


def test_bad_gemini_json_returns_ai_error(monkeypatch):
    monkeypatch.setattr(
        engine,
        "_call_gemini",
        lambda prompt: "This is not JSON",
    )

    result = analyze_job_description(sample_job_description())

    assert result["status"] == "ai_error"
    assert result["message"] == "Could not analyze job description."


def test_missing_required_gemini_fields_returns_ai_error(monkeypatch):
    bad_response = json.dumps(
        {
            "job_title": "Software Engineering Intern",
            "required_skills": ["Python"],
        }
    )

    monkeypatch.setattr(
        engine,
        "_call_gemini",
        lambda prompt: bad_response,
    )

    result = analyze_job_description(sample_job_description())

    assert result["status"] == "ai_error"
    assert result["message"] == "Could not analyze job description."