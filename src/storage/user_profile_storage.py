# src/storage/user_profile_storage.py
"""Storage layer for saved user profiles.

Architecture position:
    engine -> storage -> Google Sheets

This module stores, retrieves, lists, and deletes user profile records
in the usersProfile worksheet. It is responsible for assigning new
user IDs and converting list fields such as skills, projects, and
experience between JSON strings and Python lists.

This module should only handle persistence behavior.
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
    return get_worksheet("usersProfile")


def _parse_existing_id(value: object) -> int | None:
    text = str(value).strip().lstrip("'")

    try:
        return int(text)
    except ValueError:
        return None


def _get_next_user_id(ws) -> int:
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
    return str(left).strip().lstrip("'") == str(right).strip().lstrip("'")


def save_user_profile(user_profile: dict) -> dict:
    """Save a user profile to Google Sheets."""

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
    """Retrieve one user profile by backend user_id."""

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
    """Return all saved user profiles."""

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
    """Delete one user profile by Google Sheet row number."""

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