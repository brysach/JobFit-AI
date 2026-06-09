# src/engine/job_analysis.py

from __future__ import annotations

import json

from src.engine.gemini_client import call_gemini
from src.storage.job_analysis_storage import save_job_analysis
from src.storage.job_analysis_storage import delete_job_analysis_by_row
from src.storage.job_analysis_storage import list_job_analyses as list_job_analysis_records

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
        response_text = call_gemini(prompt)
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

def analyze_and_optionally_save(
    job_description: str,
    application_id: int | str | None = None,
    save: bool = False,
) -> dict:
    """Analyze a job description and optionally save the result."""

    response = analyze_job_description(job_description)

    if response.get("status") != "success":
        return response

    if not save:
        return response

    data = response["data"]

    job_analysis = {
        "job_title": data["job_title"],
        "required_skills": data["required_skills"],
        "keywords": data["keywords"],
    }

    save_response = save_job_analysis(job_analysis)

    response["save_status"] = save_response.get("status", "error")

    if save_response.get("status") == "success":
        response["application_id"] = save_response.get("application_id")

    return response

def list_job_analyses() -> dict:
    """Return all saved job analyses."""

    return list_job_analysis_records()


def delete_job_analysis_by_index(entry_number: int | str) -> dict:
    """Delete a saved job analysis by the displayed list number."""

    try:
        selected_index = int(entry_number)
    except ValueError:
        return {
            "status": "invalid_selection",
            "message": "Please choose a valid entry number.",
        }

    response = list_job_analysis_records()

    if response.get("status") != "success":
        return {
            "status": "storage_error",
            "message": "Could not retrieve job analyses.",
        }

    entries = response.get("data", [])

    if not entries:
        return {
            "status": "not_found",
            "message": "No job analyses were found.",
        }

    if selected_index < 1 or selected_index > len(entries):
        return {
            "status": "invalid_selection",
            "message": "Please choose a valid entry number.",
        }

    row_number = entries[selected_index - 1]["row_number"]
    delete_response = delete_job_analysis_by_row(row_number)

    if delete_response.get("status") == "success":
        return {
            "status": "success",
            "message": "Job analysis deleted successfully.",
        }

    return {
        "status": "storage_error",
        "message": "Could not delete job analysis.",
    }