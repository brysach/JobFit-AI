# src/storage/user_profile_storage.py

"""Storage layer for saved user profiles.

Architecture position:
    engine -> storage -> Google Sheets

This module stores, retrieves, lists, and deletes user profile records
in the usersProfile worksheet. It is responsible for assigning new
user IDs and converting list fields such as skills, projects, and
experience between JSON strings and Python lists.

This module should only handle persistence behavior. It should not
collect terminal input, call Gemini, generate application materials, or
format user-facing terminal output.

Google Sheet tab:
    usersProfile

Expected worksheet columns:
    user_id | name | email | phone_number | university | degree |
    skills | projects | experience

Main status contract:
    - "success": The requested storage operation completed successfully.
    - "not_found": A requested user profile record was not found.
    - "error": Required fields were missing or the Google Sheets operation failed.
"""

from __future__ import annotations

import json

from src.storage.google_sheets import get_worksheet


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


def _get_user_profile_worksheet():
    """Return the usersProfile worksheet.

    Parameters:
        None.

    Returns:
        gspread.worksheet.Worksheet: Google Sheets worksheet object for the
        usersProfile tab.

    Raises:
        Exception: If the worksheet cannot be opened.
    """

    return get_worksheet("usersProfile")


def _parse_existing_id(value: object) -> int | None:
    """Convert an existing sheet ID into an integer if possible.

    Parameters:
        value (object): Existing ID value read from Google Sheets. The value
        may be an integer, a string, or a text-formatted sheet value with a
        leading apostrophe.

    Returns:
        int | None: Parsed integer ID, or None if the value cannot be parsed.

        Possible return values:
            int:
                The parsed numeric ID.

            None:
                The value could not be converted to an integer.
    """

    text = str(value).strip().lstrip("'")

    try:
        return int(text)
    except ValueError:
        return None


def _get_next_user_id(ws) -> int:
    """Return the next available user ID.

    Parameters:
        ws (gspread.worksheet.Worksheet): usersProfile worksheet object.

    Returns:
        int: Next user ID calculated as max existing numeric ID + 1.
        If no numeric IDs exist, returns 1.
    """

    existing_ids = ws.col_values(1)
    numeric_ids = []

    for existing_id in existing_ids:
        parsed_id = _parse_existing_id(existing_id)

        if parsed_id is not None:
            numeric_ids.append(parsed_id)

    if not numeric_ids:
        return 1

    return max(numeric_ids) + 1


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


def save_user_profile(user_profile: dict) -> dict:
    """Save a user profile to Google Sheets.

    Parameters:
        user_profile (dict): User profile record prepared by the engine layer.

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
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "user_id": int,
            }

        Failure:
            {
                "status": "error",
            }

            The error status means the input was invalid, required keys were
            missing, or the Google Sheets append operation failed.

    Notes:
        skills, projects, and experience are stored as JSON strings in
        Google Sheets.
    """

    if not isinstance(user_profile, dict):
        return {"status": "error"}

    if not REQUIRED_USER_PROFILE_KEYS.issubset(user_profile.keys()):
        return {"status": "error"}

    try:
        ws = _get_user_profile_worksheet()
        user_id = _get_next_user_id(ws)

        row = [
            user_id,
            user_profile["name"],
            user_profile["email"],
            user_profile["phone_number"],
            user_profile["university"],
            user_profile["degree"],
            json.dumps(user_profile["skills"]),
            json.dumps(user_profile["projects"]),
            json.dumps(user_profile["experience"]),
        ]

        ws.append_row(row)

        return {
            "status": "success",
            "user_id": user_id,
        }
    except Exception:
        return {"status": "error"}


def get_user_profile(user_id: int | str) -> dict:
    """Retrieve one user profile by backend user ID.

    Parameters:
        user_id (int | str): Backend user ID of the saved profile to retrieve.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": {
                    "user_id": int | str,
                    "name": str,
                    "email": str,
                    "phone_number": str,
                    "university": str,
                    "degree": str,
                    "skills": list[str],
                    "projects": list[str],
                    "experience": list[str],
                },
            }

        Not found:
            {
                "status": "not_found",
                "message": "User profile was not found.",
            }

        Storage failure:
            {
                "status": "error",
                "message": "Could not retrieve user profile.",
            }

    Notes:
        skills, projects, and experience are stored as JSON strings in
        Google Sheets and converted back into Python lists before being
        returned.
    """

    try:
        ws = _get_user_profile_worksheet()
        records = ws.get_all_records()

        for record in records:
            if _ids_match(record.get("user_id"), user_id):
                return {
                    "status": "success",
                    "data": {
                        "user_id": record.get("user_id"),
                        "name": record.get("name", ""),
                        "email": record.get("email", ""),
                        "phone_number": record.get("phone_number", ""),
                        "university": record.get("university", ""),
                        "degree": record.get("degree", ""),
                        "skills": _json_to_list(record.get("skills", "[]")),
                        "projects": _json_to_list(record.get("projects", "[]")),
                        "experience": _json_to_list(record.get("experience", "[]")),
                    },
                }

        return {
            "status": "not_found",
            "message": "User profile was not found.",
        }
    except Exception:
        return {
            "status": "error",
            "message": "Could not retrieve user profile.",
        }


def list_user_profiles() -> dict:
    """Return all saved user profiles.

    Parameters:
        None.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "data": [
                    {
                        "row_number": int,
                        "user_id": int | str,
                        "name": str,
                        "email": str,
                        "phone_number": str,
                        "university": str,
                        "degree": str,
                        "skills": list[str],
                        "projects": list[str],
                        "experience": list[str],
                    }
                ],
            }

        Storage failure:
            {
                "status": "error",
                "message": "Could not retrieve user profiles.",
            }

    Notes:
        The row_number value is the actual Google Sheets row number.
        It is used internally for deletion and should not be treated as
        the same thing as user_id.
    """

    try:
        ws = _get_user_profile_worksheet()
        records = ws.get_all_records()

        user_profiles = []

        for index, record in enumerate(records, start=2):
            user_profiles.append(
                {
                    "row_number": index,
                    "user_id": record.get("user_id"),
                    "name": record.get("name", ""),
                    "email": record.get("email", ""),
                    "phone_number": record.get("phone_number", ""),
                    "university": record.get("university", ""),
                    "degree": record.get("degree", ""),
                    "skills": _json_to_list(record.get("skills", "[]")),
                    "projects": _json_to_list(record.get("projects", "[]")),
                    "experience": _json_to_list(record.get("experience", "[]")),
                }
            )

        return {
            "status": "success",
            "data": user_profiles,
        }
    except Exception:
        return {
            "status": "error",
            "message": "Could not retrieve user profiles.",
        }


def delete_user_profile_by_row(row_number: int) -> dict:
    """Delete one user profile by Google Sheets row number.

    Parameters:
        row_number (int): Actual row number in the usersProfile worksheet.

    Returns:
        dict: Response payload with one of these possible statuses:

        Success:
            {
                "status": "success",
                "message": "User profile deleted successfully.",
            }

        Storage failure:
            {
                "status": "error",
                "message": "Could not delete user profile.",
            }

    Notes:
        This function expects a Google Sheets row number, not a user_id and
        not the displayed list number shown in the interface.
    """

    try:
        ws = _get_user_profile_worksheet()
        ws.delete_rows(row_number)

        return {
            "status": "success",
            "message": "User profile deleted successfully.",
        }
    except Exception:
        return {
            "status": "error",
            "message": "Could not delete user profile.",
        }