# src/engine/materials.py

from __future__ import annotations

import json

from src.engine.gemini_client import call_gemini
from src.storage.job_analysis_storage import get_job_analysis
from src.storage.materials_storage import save_generated_materials as save_generated_materials_record
from src.storage.user_profile_storage import get_user_profile


REQUIRED_USER_PROFILE_KEYS = {
    "name",
    "email",
    "phone_number",
    "university",
    "degree",
    "skills",
    "projects",
    "experience",
}

REQUIRED_JOB_ANALYSIS_KEYS = {
    "company_name",
    "job_title",
    "required_skills",
    "keywords",
}

REQUIRED_MATERIALS_KEYS = {
    "resume",
    "cover_letter",
    "strengths",
    "weaknesses",
}

_MATERIALS_PROMPT = """
You are helping generate professional application materials.

Use ONLY the user's provided background.
Do not invent experience, skills, education, projects, or achievements.

Return ONLY valid JSON with these keys:
- resume: object with these keys:
  - skills: list of strings
  - projects: list of strings
  - experience: list of strings
- cover_letter: string
- strengths: list of strings
- weaknesses: list of strings

Resume instructions:
- The resume content will later be inserted into a professional .docx template.
- Do not include the user's name, email, phone number, university, or degree in the generated resume object.
- For resume.skills, choose or rewrite skill bullets based only on the user's provided skills and the job analysis.
- For resume.projects, write strong resume bullets based only on the user's provided projects and the job analysis.
- For resume.experience, write strong resume bullets based only on the user's provided experience and the job analysis.
- Keep resume bullets concise, professional, and matched to the job.

Cover letter instructions:
- The cover letter should be professional, concise, and tailored to the job.
- If the job analysis includes a company_name other than "Unknown", refer to the company by name when it sounds natural.
- If the company_name is "Unknown", use a general greeting such as "Dear Hiring Team".

Strengths instructions:
- List the user's strongest matches for this job.
- Explain how the user can use those strengths in an interview, resume discussion, or assessment.
- Keep each strength practical and specific.

Weaknesses instructions:
- List the user's weakest areas or missing requirements for this job.
- Explain how the user can prepare for those weaknesses before an interview or assessment test.
- Be honest but constructive.
- Do not shame the user.

User profile:
{user_profile}

Job analysis:
{job_analysis}
"""


def _clean_json_response(text: str) -> str:
    cleaned_text = text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.removeprefix("```json").strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```").strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text.removesuffix("```").strip()

    return cleaned_text


def _is_string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_valid_user_profile(user_profile: dict) -> bool:
    if not isinstance(user_profile, dict):
        return False

    if not REQUIRED_USER_PROFILE_KEYS.issubset(user_profile.keys()):
        return False

    string_keys = {
        "name",
        "email",
        "phone_number",
        "university",
        "degree",
    }

    for key in string_keys:
        if not isinstance(user_profile[key], str) or user_profile[key].strip() == "":
            return False

    list_keys = {
        "skills",
        "projects",
        "experience",
    }

    for key in list_keys:
        if not _is_string_list(user_profile[key]):
            return False

    return True


def _is_valid_job_analysis(job_analysis: dict) -> bool:
    if not isinstance(job_analysis, dict):
        return False

    if not REQUIRED_JOB_ANALYSIS_KEYS.issubset(job_analysis.keys()):
        return False

    if not isinstance(job_analysis["company_name"], str):
        return False

    if not isinstance(job_analysis["job_title"], str):
        return False

    if not _is_string_list(job_analysis["required_skills"]):
        return False

    if not _is_string_list(job_analysis["keywords"]):
        return False

    return True


def _parse_materials_response(text: str) -> dict | None:
    cleaned_text = _clean_json_response(text)

    try:
        data = json.loads(cleaned_text)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    if not REQUIRED_MATERIALS_KEYS.issubset(data.keys()):
        return None

    resume = data["resume"]

    if not isinstance(resume, dict):
        return None

    resume_keys = {
        "skills",
        "projects",
        "experience",
    }

    if not resume_keys.issubset(resume.keys()):
        return None

    if not _is_string_list(resume["skills"]):
        return None

    if not _is_string_list(resume["projects"]):
        return None

    if not _is_string_list(resume["experience"]):
        return None

    if not isinstance(data["cover_letter"], str):
        return None

    if not _is_string_list(data["strengths"]):
        return None

    if not _is_string_list(data["weaknesses"]):
        return None

    return {
        "resume": {
            "skills": resume["skills"],
            "projects": resume["projects"],
            "experience": resume["experience"],
        },
        "cover_letter": data["cover_letter"],
        "strengths": data["strengths"],
        "weaknesses": data["weaknesses"],
    }


def generate_application_materials(user_profile: dict, job_analysis: dict) -> dict:
    """Generate structured resume content, cover letter, strengths, and weaknesses."""

    if not _is_valid_user_profile(user_profile):
        return {
            "status": "incomplete_profile",
            "message": "User profile is required before generating materials.",
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
        gemini_response = call_gemini(prompt)
    except Exception:
        return {
            "status": "ai_error",
            "message": "Could not generate application materials.",
        }

    materials_data = _parse_materials_response(gemini_response)

    if materials_data is None:
        return {
            "status": "generation_failed",
            "message": "Could not understand the generated materials.",
        }

    return {
        "status": "success",
        "data": materials_data,
    }


def generate_materials_for_saved_records(
    user_id: int | str,
    application_id: int | str,
    save: bool = False,
) -> dict:
    """Generate materials from saved user and job records."""

    user_response = get_user_profile(user_id)

    if user_response.get("status") != "success":
        return user_response

    job_response = get_job_analysis(application_id)

    if job_response.get("status") != "success":
        return job_response

    user_profile = user_response["data"]
    job_analysis = job_response["data"]

    response = generate_application_materials(user_profile, job_analysis)

    if response.get("status") != "success":
        return response

    if save:
        data = response["data"]

        save_record = {
            "application_id": application_id,
            "user_id": user_id,
            "resume_skills": data["resume"]["skills"],
            "resume_projects": data["resume"]["projects"],
            "resume_experience": data["resume"]["experience"],
            "cover_letter": data["cover_letter"],
            "strengths": data["strengths"],
            "weaknesses": data["weaknesses"],
        }

        save_status = save_generated_materials_record(save_record)
        response["save_status"] = save_status

    return response