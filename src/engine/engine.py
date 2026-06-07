# src/engine/engine.py

from __future__ import annotations

import json


REQUIRED_ANALYSIS_KEYS = {
    "job_title",
    "required_skills",
    "preferred_skills",
    "responsibilities",
    "keywords",
}


_EXTRACTION_PROMPT = """
Analyze the following job description.

Return ONLY valid JSON with these keys:
- job_title: string
- required_skills: list of strings
- preferred_skills: list of strings
- responsibilities: list of strings
- keywords: list of strings

Job description:
{job_description}
"""


def _looks_like_job_description(text: str) -> bool:
    """Return True if the text appears to describe a job."""
    lowered = text.lower()

    job_terms = [
        "job",
        "position",
        "role",
        "responsibilities",
        "requirements",
        "qualifications",
        "experience",
        "skills",
        "candidate",
        "company",
        "apply",
    ]

    return any(term in lowered for term in job_terms)


def _call_gemini(prompt: str) -> str:
    """Call Gemini API and return the raw response text.

    This is intentionally not implemented yet.
    Tests should mock this function.
    """
    raise RuntimeError("Gemini API call is not implemented yet.")


def _parse_analysis_response(response_text: str) -> dict | None:
    """Parse and validate Gemini's JSON response."""
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    if not all(key in data for key in REQUIRED_ANALYSIS_KEYS):
        return None

    if not isinstance(data["job_title"], str):
        return None

    list_keys = [
        "required_skills",
        "preferred_skills",
        "responsibilities",
        "keywords",
    ]

    for key in list_keys:
        if not isinstance(data[key], list):
            return None

    return data


def analyze_job_description(job_description: str) -> dict:
    """Analyze a job description and return structured data."""

    if not job_description or not job_description.strip():
        return {
            "status": "incomplete",
            "message": "Job description is required.",
        }

    if not _looks_like_job_description(job_description):
        return {
            "status": "invalid_input",
            "message": "Input does not appear to be a job description.",
        }

    prompt = _EXTRACTION_PROMPT.format(job_description=job_description)

    try:
        response_text = _call_gemini(prompt)
    except Exception:
        return {
            "status": "ai_error",
            "message": "Could not analyze job description.",
        }

    data = _parse_analysis_response(response_text)

    if data is None:
        return {
            "status": "ai_error",
            "message": "Could not analyze job description.",
        }

    return {
        "status": "success",
        "data": data,
    }