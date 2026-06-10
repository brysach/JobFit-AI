# src/engine/materials.py

"""Engine layer for generating application materials.

Architecture position:
    interface -> engine -> storage
              -> export

This module retrieves saved user profiles and job analyses, validates
that both records contain the required fields, asks Gemini to generate
tailored application materials, and optionally saves the generated
materials through the storage layer.

Generated materials include structured resume sections, a cover letter,
strengths for the target job, and weaknesses with preparation advice.
The module returns response dictionaries with a "status" field instead
of printing output directly.

Main status contract:
    - "success": Application materials were generated successfully.
    - "incomplete_profile": The user profile is missing required fields.
    - "missing_job_analysis": The job analysis is missing required fields.
    - "ai_error": Gemini failed while generating materials.
    - "generation_failed": Gemini returned invalid or badly formatted output.
    - "not_found": A saved user profile or job analysis was not found.
    - "error": Storage could not retrieve or save the requested data.

Saved materials status contract:
    - "success": Generated materials were saved successfully.
    - "exists": Generated materials already exist for that user and job.
    - "error": Generated materials could not be saved.
"""

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
    """Remove Markdown code fences from Gemini JSON output.

    Parameters:
        text (str): Raw Gemini response text.

    Returns:
        str: Cleaned response text with surrounding Markdown code fences
        removed when they are present.
    """

    cleaned_text = text.strip()

    if cleaned_text.startswith("```json"):
        cleaned_text = cleaned_text.removeprefix("```json").strip()

    if cleaned_text.startswith("```"):
        cleaned_text = cleaned_text.removeprefix("```").strip()

    if cleaned_text.endswith("```"):
        cleaned_text = cleaned_text.removesuffix("```").strip()

    return cleaned_text


def _is_string_list(value: object) -> bool:
    """Return True if a value is a list containing only strings.

    Parameters:
        value (object): Value to validate.

    Returns:
        bool: True if value is a list and every item in the list is a
        string; otherwise, False.
    """

    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _is_valid_user_profile(user_profile: dict) -> bool:
    """Validate that a user profile has the required application fields.

    Parameters:
        user_profile (dict): User profile data retrieved from storage or
        passed directly into the engine.

        Expected format:
            {
                "name": str,
                "email": str,
                "phone_number": str,
                "university": str,
                "degree": str,
                "skills": list[str],
                "projects": list[str],
                "experience": list[str],
            }

    Returns:
        bool: True if the profile contains all required fields with valid
        types; otherwise, False.
    """

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
    """Validate that a job analysis has the required application fields.

    Parameters:
        job_analysis (dict): Job analysis data retrieved from storage or
        passed directly into the engine.

        Expected format:
            {
                "company_name": str,
                "job_title": str,
                "required_skills": list[str],
                "keywords": list[str],
            }

    Returns:
        bool: True if the job analysis contains all required fields with
        valid types; otherwise, False.
    """

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
    """Parse and validate Gemini's generated materials response.

    Parameters:
        text (str): Raw Gemini response text.

    Returns:
        dict | None: A validated generated materials dictionary if Gemini
        returned usable JSON with all required fields; otherwise, None.

        Successful dictionary format:
            {
                "resume": {
                    "skills": list[str],
                    "projects": list[str],
                    "experience": list[str],
                },
                "cover_letter": str,
                "strengths": list[str],
                "weaknesses": list[str],
            }
    """

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
    """Generate structured resume content, cover letter, strengths, and weaknesses.

    Parameters:
        user_profile (dict): User profile data containing the user's contact
        information, education information, skills, projects, and experience.

        job_analysis (dict): Job analysis data containing the company name,
        job title, required skills, and keywords.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": {
                    "resume": {
                        "skills": list[str],
                        "projects": list[str],
                        "experience": list[str],
                    },
                    "cover_letter": str,
                    "strengths": list[str],
                    "weaknesses": list[str],
                },
            }

        Failure:
            {
                "status": "incomplete_profile",
                "message": "User profile is required before generating materials.",
            }

            {
                "status": "missing_job_analysis",
                "message": "Job analysis is required before generating materials.",
            }

            {
                "status": "ai_error",
                "message": "Could not generate application materials.",
            }

            {
                "status": "generation_failed",
                "message": "Could not understand the generated materials.",
            }
    """

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
    """Generate materials from saved user and job records.

    Parameters:
        user_id (int | str): ID of the saved user profile to retrieve from
        storage.

        application_id (int | str): ID of the saved job analysis to retrieve
        from storage.

        save (bool): True if the generated materials should be saved in
        storage; otherwise, False.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success without saving:
            {
                "status": "success",
                "data": {
                    "resume": {
                        "skills": list[str],
                        "projects": list[str],
                        "experience": list[str],
                    },
                    "cover_letter": str,
                    "strengths": list[str],
                    "weaknesses": list[str],
                },
            }

        Success with saving:
            {
                "status": "success",
                "data": {
                    "resume": {
                        "skills": list[str],
                        "projects": list[str],
                        "experience": list[str],
                    },
                    "cover_letter": str,
                    "strengths": list[str],
                    "weaknesses": list[str],
                },
                "save_status": "success" | "exists" | "error",
            }

        Failure from retrieving saved records:
            {
                "status": "not_found",
                "message": str,
            }

            {
                "status": "error",
                "message": str,
            }

        Failure from generating materials:
            Returns the same failure payloads as
            generate_application_materials().
    """

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