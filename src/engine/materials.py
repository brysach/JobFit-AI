# src/engine/materials.py

from __future__ import annotations

import json

from src.engine.gemini_client import call_gemini
from src.storage.job_analysis_storage import get_job_analysis as get_job_analysis_record
from src.storage.materials_storage import save_generated_materials as save_generated_materials_record
from src.storage.user_profile_storage import get_user_profile as get_user_profile_record


REQUIRED_USER_PROFILE_KEYS = {
    "name",
    "education",
    "skills",
    "projects",
    "experience",
}

REQUIRED_JOB_ANALYSIS_KEYS = {
    "job_title",
    "required_skills",
    "keywords",
}

REQUIRED_GENERATED_MATERIALS_KEYS = {
    "resume_bullets",
    "cover_letter",
    "warnings",
}


_MATERIALS_PROMPT = """
You are helping generate application materials.

Use ONLY the user's provided background.
Do not invent experience, skills, education, projects, or achievements.

Return ONLY valid JSON with these keys:
- resume_bullets: list of strings
- cover_letter: string
- warnings: list of strings

The resume bullets should be strong, specific, and matched to the job.
The cover letter should be professional, concise, and tailored to the job.
The warnings list should mention any job requirements that are weakly supported or missing from the user's profile.

User profile:
{user_profile}

Job analysis:
{job_analysis}
"""


def _is_non_empty_string(value) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _is_non_empty_list(value) -> bool:
    return isinstance(value, list) and len(value) > 0


def _is_valid_user_profile(user_profile: dict) -> bool:
    """Return True if the user profile has enough information."""

    if not isinstance(user_profile, dict):
        return False

    if not all(key in user_profile for key in REQUIRED_USER_PROFILE_KEYS):
        return False

    if not _is_non_empty_string(user_profile["name"]):
        return False

    if not _is_non_empty_string(user_profile["education"]):
        return False

    if not _is_non_empty_list(user_profile["skills"]):
        return False

    if not _is_non_empty_list(user_profile["projects"]):
        return False

    if not _is_non_empty_list(user_profile["experience"]):
        return False

    return True


def _is_valid_job_analysis(job_analysis: dict) -> bool:
    """Return True if the job analysis has enough information."""

    if not isinstance(job_analysis, dict):
        return False

    if not all(key in job_analysis for key in REQUIRED_JOB_ANALYSIS_KEYS):
        return False

    if not _is_non_empty_string(job_analysis["job_title"]):
        return False

    if not _is_non_empty_list(job_analysis["required_skills"]):
        return False

    if not isinstance(job_analysis["keywords"], list):
        return False

    return True


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


def _parse_materials_response(response_text: str) -> dict | None:
    """Parse and validate Gemini's generated materials response."""

    cleaned_text = _clean_json_response(response_text)

    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    if not all(key in data for key in REQUIRED_GENERATED_MATERIALS_KEYS):
        return None

    if not _is_non_empty_list(data["resume_bullets"]):
        return None

    if not _is_non_empty_string(data["cover_letter"]):
        return None

    if not isinstance(data["warnings"], list):
        return None

    return data


def generate_application_materials(user_profile: dict, job_analysis: dict) -> dict:
    """Generate resume bullets and a cover letter from profile and job data."""

    if not _is_valid_user_profile(user_profile):
        return {
            "status": "incomplete_profile",
            "message": "User profile is missing required information.",
        }

    if not _is_valid_job_analysis(job_analysis):
        return {
            "status": "missing_job_analysis",
            "message": "Job analysis is required before generating materials.",
        }

    prompt = _MATERIALS_PROMPT.format(
        user_profile=json.dumps(user_profile, indent=2),
        job_analysis=json.dumps(job_analysis, indent=2),
    )

    try:
        response_text = call_gemini(prompt)
    except Exception:
        return {
            "status": "ai_error",
            "message": "Could not generate application materials.",
        }

    data = _parse_materials_response(response_text)

    if data is None:
        return {
            "status": "generation_failed",
            "message": "Generated content was empty or invalid.",
        }

    return {
        "status": "success",
        "data": data,
    }


def generate_materials_for_saved_records(
    user_id: int | str,
    application_id: int | str,
    save: bool = False,
) -> dict:
    """Generate materials using saved user profile and saved job analysis.

    This keeps the architecture flow as:
    interface -> engine -> storage
    """

    if user_id is None or str(user_id).strip() == "":
        return {
            "status": "incomplete_profile",
            "message": "User profile is missing required information.",
        }

    if application_id is None or str(application_id).strip() == "":
        return {
            "status": "missing_job_analysis",
            "message": "Job analysis is required before generating materials.",
        }

    user_profile_response = get_user_profile_record(user_id)

    if user_profile_response.get("status") != "success":
        return {
            "status": "incomplete_profile",
            "message": "User profile is missing required information.",
        }

    job_analysis_response = get_job_analysis_record(application_id)

    if job_analysis_response.get("status") != "success":
        return {
            "status": "missing_job_analysis",
            "message": "Job analysis is required before generating materials.",
        }

    user_profile = user_profile_response["data"]
    job_analysis = job_analysis_response["data"]

    response = generate_application_materials(user_profile, job_analysis)

    if response.get("status") != "success":
        return response

    if not save:
        return response

    materials = {
        "application_id": application_id,
        "user_id": user_id,
        "resume_bullets": response["data"]["resume_bullets"],
        "cover_letter": response["data"]["cover_letter"],
    }

    save_status = save_generated_materials_record(materials)

    response["save_status"] = save_status

    return response