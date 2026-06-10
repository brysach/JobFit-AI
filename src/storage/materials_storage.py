# src/storage/materials_storage.py

"""Storage layer for generated application materials.

Architecture position:
    engine -> storage -> Google Sheets

This module stores and retrieves generated resume sections, cover
letters, strengths, and weaknesses in the generatedMaterials worksheet.
It prevents duplicate saved materials for the same user and job
combination.

This module does not generate AI content and does not format terminal
output.

Google Sheet tab:
    generatedMaterials

Expected worksheet columns:
    application_id | user_id | resume_skills | resume_projects |
    resume_experience | cover_letter | strengths | weaknesses

Main status contract:
    - "success": Generated materials were saved or retrieved successfully.
    - "exists": Generated materials already exist for the same user and job.
    - "not_found": No generated materials matched the requested IDs.
    - "error": Required fields were missing or the Google Sheets operation failed.
"""

from __future__ import annotations

import json

from src.storage.google_sheets import get_worksheet


REQUIRED_GENERATED_MATERIALS_KEYS = {
    "application_id",
    "user_id",
    "resume_skills",
    "resume_projects",
    "resume_experience",
    "cover_letter",
    "strengths",
    "weaknesses",
}


def _get_generated_materials_worksheet():
    """Return the generatedMaterials worksheet.

    Parameters:
        None.

    Returns:
        gspread.worksheet.Worksheet: Google Sheets worksheet object for the
        generatedMaterials tab.

    Raises:
        Exception: If the worksheet cannot be opened.
    """

    return get_worksheet("generatedMaterials")


def _json_to_list(value: object) -> list[str]:
    """Convert a stored JSON value into a list of strings.

    Parameters:
        value (object): Value read from Google Sheets. This is expected to be
        a JSON-encoded list, but it may be another value if the sheet data is
        malformed.

    Returns:
        list[str]: Parsed list of string values.

        Possible return values:
            list[str]:
                Returned when value contains a valid JSON list.

            []:
                Returned when value is not valid JSON, when value cannot be
                parsed, or when the parsed JSON value is not a list.
    """

    if not isinstance(value, str):
        value = str(value)

    try:
        data = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(data, list):
        return []

    return [str(item) for item in data]


def _ids_match(left: object, right: object) -> bool:
    """Compare two backend IDs after normalizing their text form.

    Parameters:
        left (object): First ID value to compare.
        right (object): Second ID value to compare.

    Returns:
        bool: True if both IDs match after converting to strings, removing
        surrounding whitespace, and removing a leading apostrophe used by
        Google Sheets text formatting; otherwise, False.
    """

    return str(left).strip().lstrip("'") == str(right).strip().lstrip("'")


def save_generated_materials(materials: dict) -> str:
    """Save generated resume, cover letter, strengths, and weaknesses.

    Parameters:
        materials (dict): Generated materials record prepared by the engine
        layer.

        Expected format:
            {
                "application_id": int | str,
                "user_id": int | str,
                "resume_skills": list[str],
                "resume_projects": list[str],
                "resume_experience": list[str],
                "cover_letter": str,
                "strengths": list[str],
                "weaknesses": list[str],
            }

    Returns:
        str: Save status.

        Possible return values:
            "success":
                The generated materials were saved successfully.

            "exists":
                A generated materials record already exists for the same
                application_id and user_id.

            "error":
                The input was invalid, required keys were missing, or the
                Google Sheets operation failed.
    """

    if not isinstance(materials, dict):
        return "error"

    if not REQUIRED_GENERATED_MATERIALS_KEYS.issubset(materials.keys()):
        return "error"

    try:
        ws = _get_generated_materials_worksheet()
        records = ws.get_all_records()

        for record in records:
            same_application = _ids_match(
                record.get("application_id"),
                materials["application_id"],
            )
            same_user = _ids_match(
                record.get("user_id"),
                materials["user_id"],
            )

            if same_application and same_user:
                return "exists"

        row = [
            materials["application_id"],
            materials["user_id"],
            json.dumps(materials["resume_skills"]),
            json.dumps(materials["resume_projects"]),
            json.dumps(materials["resume_experience"]),
            materials["cover_letter"],
            json.dumps(materials["strengths"]),
            json.dumps(materials["weaknesses"]),
        ]

        ws.append_row(row)

        return "success"
    except Exception:
        return "error"


def get_generated_materials(
    application_id: int | str,
    user_id: int | str | None = None,
) -> dict:
    """Retrieve generated materials by application ID and optional user ID.

    Parameters:
        application_id (int | str): Application ID of the saved generated
        materials record.

        user_id (int | str | None): Optional user ID used to narrow the search.
        If None, the first record matching application_id is returned.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": {
                    "application_id": int | str,
                    "user_id": int | str,
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

        Not found:
            {
                "status": "not_found",
                "message": "Generated materials were not found.",
            }

        Storage failure:
            {
                "status": "error",
                "message": "Could not retrieve generated materials.",
            }

    Notes:
        The resume_skills, resume_projects, resume_experience, strengths,
        and weaknesses fields are stored as JSON strings in Google Sheets and
        converted back into Python lists before being returned.
    """

    try:
        ws = _get_generated_materials_worksheet()
        records = ws.get_all_records()

        for record in records:
            application_matches = _ids_match(
                record.get("application_id"),
                application_id,
            )

            if not application_matches:
                continue

            if user_id is not None and not _ids_match(record.get("user_id"), user_id):
                continue

            return {
                "status": "success",
                "data": {
                    "application_id": record.get("application_id"),
                    "user_id": record.get("user_id"),
                    "resume": {
                        "skills": _json_to_list(record.get("resume_skills", "[]")),
                        "projects": _json_to_list(
                            record.get("resume_projects", "[]")
                        ),
                        "experience": _json_to_list(
                            record.get("resume_experience", "[]")
                        ),
                    },
                    "cover_letter": record.get("cover_letter", ""),
                    "strengths": _json_to_list(record.get("strengths", "[]")),
                    "weaknesses": _json_to_list(record.get("weaknesses", "[]")),
                },
            }

        return {
            "status": "not_found",
            "message": "Generated materials were not found.",
        }
    except Exception:
        return {
            "status": "error",
            "message": "Could not retrieve generated materials.",
        }