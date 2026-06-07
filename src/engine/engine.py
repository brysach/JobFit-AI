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
    """Call Gemini API and return the raw response text."""

    import os
    from google import genai

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError("GEMINI_API_KEY environment variable is missing.")

    model_name = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    client = genai.Client(api_key=api_key)

    try:
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
        )

        if not response.text:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text
    finally:
        client.close()

def _clean_json_response(response_text: str) -> str:
    """Remove Markdown code fences from Gemini JSON output."""

    text = response_text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()

    if text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text

def _parse_analysis_response(response_text: str) -> dict | None:
    """Parse and validate Gemini's JSON response."""

    cleaned_text = _clean_json_response(response_text)

    try:
        data = json.loads(cleaned_text)
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
    except Exception as error:
        print("DEBUG Gemini call failed:", error)
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