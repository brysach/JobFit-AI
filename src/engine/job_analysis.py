# src/engine/job_analysis.py

"""Engine layer for analyzing job descriptions.

Architecture position:
    interface -> engine -> storage

This module receives a raw job description from the interface layer,
uses Gemini to extract structured job information, validates the
generated response, and optionally sends the saved job analysis record
to the storage layer.

This module does not read terminal input and does not directly format
terminal output. It returns response dictionaries with a "status" field
so the interface layer can decide what to display.

Main status contract:
    - "success": The job description was analyzed or saved successfully.
    - "incomplete": The job description was empty.
    - "invalid_input": The input did not appear to describe a job.
    - "ai_error": Gemini failed or returned unusable output.
    - "storage_error": The job analysis could not be saved or deleted.
    - "not_found": No saved job analyses were found.
    - "invalid_selection": The user selected an invalid list entry.
"""

from __future__ import annotations

import json

from src.engine.gemini_client import call_gemini
from src.storage.job_analysis_storage import delete_job_analysis_by_row
from src.storage.job_analysis_storage import list_job_analyses as list_job_analysis_records
from src.storage.job_analysis_storage import save_job_analysis


REQUIRED_ANALYSIS_KEYS = {
    "company_name",
    "job_title",
    "required_skills",
    "preferred_skills",
    "responsibilities",
    "keywords",
}


_EXTRACTION_PROMPT = """
Analyze the following job description.

Return ONLY valid JSON with these keys:
- company_name: string
- job_title: string
- required_skills: list of strings
- preferred_skills: list of strings
- responsibilities: list of strings
- keywords: list of strings

If the company name is not clearly stated, use "Unknown".

Job description:
{job_description}
"""


def _looks_like_job_description(text: str) -> bool:
    """Return True if the text appears to describe a job.

    Parameters:
        text (str): Raw text entered by the user.

    Returns:
        bool: True if the text contains common job-description terms;
        otherwise, False.
    """

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
    """Remove Markdown code fences from Gemini JSON output.

    Parameters:
        response_text (str): Raw Gemini response text.

    Returns:
        str: Cleaned response text with surrounding Markdown code fences
        removed when they are present.
    """

    text = response_text.strip()

    if text.startswith("```json"):
        text = text.removeprefix("```json").strip()

    if text.startswith("```"):
        text = text.removeprefix("```").strip()

    if text.endswith("```"):
        text = text.removesuffix("```").strip()

    return text


def _parse_analysis_response(response_text: str) -> dict | None:
    """Parse and validate Gemini's JSON job analysis response.

    Parameters:
        response_text (str): Raw Gemini response text.

    Returns:
        dict | None: A validated job analysis dictionary if Gemini returned
        usable JSON with all required fields; otherwise, None.

        Successful dictionary format:
            {
                "company_name": str,
                "job_title": str,
                "required_skills": list,
                "preferred_skills": list,
                "responsibilities": list,
                "keywords": list,
            }
    """

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
        if not isinstance(data["company_name"], str):
            return None

    return data


def analyze_job_description(job_description: str) -> dict:
    """Analyze a job description and return structured job data.

    Parameters:
        job_description (str): Raw job posting text entered by the user.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": {
                    "company_name": str,
                    "job_title": str,
                    "required_skills": list[str],
                    "preferred_skills": list[str],
                    "responsibilities": list[str],
                    "keywords": list[str],
                },
            }

        Failure:
            {
                "status": "incomplete",
                "message": "Job description is required.",
            }

            {
                "status": "invalid_input",
                "message": "Input does not appear to be a job description.",
            }

            {
                "status": "ai_error",
                "message": "Could not analyze job description.",
            }
    """

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
    """Analyze a job description and optionally save the result.

    Parameters:
        job_description (str): Raw job posting text entered by the user.
        application_id (int | str | None): Optional application ID value.
            This parameter is accepted for compatibility with the contract,
            but new saved records generate their own ID in storage.
        save (bool): True if the analyzed job description should be saved;
            otherwise, False.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success without saving:
            {
                "status": "success",
                "data": {
                    "company_name": str,
                    "job_title": str,
                    "required_skills": list[str],
                    "preferred_skills": list[str],
                    "responsibilities": list[str],
                    "keywords": list[str],
                },
            }

        Success with saving:
            {
                "status": "success",
                "data": {
                    "company_name": str,
                    "job_title": str,
                    "required_skills": list[str],
                    "preferred_skills": list[str],
                    "responsibilities": list[str],
                    "keywords": list[str],
                },
                "save_status": "success",
                "application_id": int,
            }

        Save failure after successful analysis:
            {
                "status": "success",
                "data": dict,
                "save_status": "error",
            }

        Analysis failure:
            Returns the same failure payloads as analyze_job_description().
    """

    response = analyze_job_description(job_description)

    if response.get("status") != "success":
        return response

    if not save:
        return response

    data = response["data"]

    job_analysis = {
        "company_name": data.get("company_name", "Unknown"),
        "job_title": data["job_title"],
        "required_skills": data["required_skills"],
        "keywords": data["keywords"],
    }

    save_response = save_job_analysis(job_analysis)

    response["save_status"] = save_response.get("status", "error")

    if save_response.get("status") == "success":
        response["application_id"] = save_response.get("application_id")

    return response


def save_existing_job_analysis(analysis_data: dict) -> dict:
    """Save an already generated job analysis.

    Parameters:
        analysis_data (dict): Structured job analysis produced by
        analyze_job_description().

        Expected format:
            {
                "company_name": str,
                "job_title": str,
                "required_skills": list[str],
                "preferred_skills": list[str],
                "responsibilities": list[str],
                "keywords": list[str],
            }

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "save_status": "success",
                "application_id": int,
            }

        Failure:
            {
                "status": "storage_error",
                "message": "Could not save job analysis.",
            }
    """

    if not isinstance(analysis_data, dict):
        return {
            "status": "storage_error",
            "message": "Could not save job analysis.",
        }

    required_keys = {
        "job_title",
        "required_skills",
        "keywords",
    }

    if not all(key in analysis_data for key in required_keys):
        return {
            "status": "storage_error",
            "message": "Could not save job analysis.",
        }

    job_analysis = {
        "company_name": analysis_data.get("company_name", "Unknown"),
        "job_title": analysis_data["job_title"],
        "required_skills": analysis_data["required_skills"],
        "keywords": analysis_data["keywords"],
    }

    save_response = save_job_analysis(job_analysis)

    if save_response.get("status") == "success":
        return {
            "status": "success",
            "save_status": "success",
            "application_id": save_response.get("application_id"),
        }

    return {
        "status": "storage_error",
        "message": "Could not save job analysis.",
    }


def list_job_analyses() -> dict:
    """Return all saved job analyses.

    Parameters:
        None.

    Returns:
        dict: Response payload returned by the storage layer.

        Success:
            {
                "status": "success",
                "data": [
                    {
                        "row_number": int,
                        "application_id": int | str,
                        "company_name": str,
                        "job_title": str,
                        "required_skills": list[str],
                        "keywords": list[str],
                    }
                ],
            }

        Failure:
            {
                "status": "not_found",
                "message": "No job analyses were found.",
            }

            {
                "status": "error",
                "message": str,
            }
    """

    return list_job_analysis_records()


def delete_job_analysis_by_index(entry_number: int | str) -> dict:
    """Delete a saved job analysis by the displayed list number.

    Parameters:
        entry_number (int | str): The list number displayed to the user
        in the interface layer.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "message": "Job analysis deleted successfully.",
            }

        Failure:
            {
                "status": "invalid_selection",
                "message": "Please choose a valid entry number.",
            }

            {
                "status": "not_found",
                "message": "No job analyses were found.",
            }

            {
                "status": "storage_error",
                "message": "Could not retrieve job analyses.",
            }

            {
                "status": "storage_error",
                "message": "Could not delete job analysis.",
            }
    """

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