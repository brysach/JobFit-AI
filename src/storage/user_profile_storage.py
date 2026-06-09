# src/storage/user_profile_storage.py

from __future__ import annotations

import json

from src.storage.google_sheets import get_worksheet


REQUIRED_USER_PROFILE_KEYS = {
    "name",
    "education",
    "skills",
    "projects",
    "experience",
}


def _list_to_json(items: list[str]) -> str:
    """Convert a list of strings to a JSON string for Google Sheets."""

    return json.dumps(items)


def _json_to_list(value: object) -> list[str]:
    """Convert a JSON string from Google Sheets back to a list of strings."""

    if not isinstance(value, str):
        value = str(value)

    try:
        data = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(data, list):
        return []

    return [str(item) for item in data]


def _parse_existing_id(value: object) -> int | None:
    """Convert an existing sheet ID into an int if possible."""

    text = str(value).strip().lstrip("'")

    try:
        return int(text)
    except ValueError:
        return None


def _get_next_user_id(ws) -> int:
    """Return the next user_id using max existing ID + 1."""

    existing_ids = ws.col_values(1)
    numeric_ids = []

    for existing_id in existing_ids:
        parsed_id = _parse_existing_id(existing_id)

        if parsed_id is not None:
            numeric_ids.append(parsed_id)

    if not numeric_ids:
        return 1

    return max(numeric_ids) + 1


def save_user_profile(user_profile: dict) -> dict:
    """Save user profile data."""

    if not all(key in user_profile for key in REQUIRED_USER_PROFILE_KEYS):
        return {"status": "error"}

    try:
        ws = get_worksheet("usersProfile")

        user_id = _get_next_user_id(ws)

        row = [
            user_id,
            user_profile["name"],
            user_profile["education"],
            _list_to_json(user_profile["skills"]),
            _list_to_json(user_profile["projects"]),
            _list_to_json(user_profile["experience"]),
        ]

        ws.append_row(row)

        return {
            "status": "success",
            "user_id": user_id,
        }
    except Exception:
        return {"status": "error"}


def get_user_profile(user_id: int | str) -> dict:
    """Retrieve a user profile by user_id."""

    try:
        ws = get_worksheet("usersProfile")
        records = ws.get_all_records()

        for record in records:
            if str(record.get("user_id")) == str(user_id):
                return {
                    "status": "success",
                    "data": {
                        "user_id": record.get("user_id"),
                        "name": record.get("name", ""),
                        "education": record.get("education", ""),
                        "skills": _json_to_list(record.get("skills", "")),
                        "projects": _json_to_list(record.get("projects", "")),
                        "experience": _json_to_list(record.get("experience", "")),
                    },
                }

        return {
            "status": "not_found",
            "message": "User profile was not found.",
        }
    except Exception:
        return {
            "status": "not_found",
            "message": "User profile was not found.",
        }


def list_user_profiles() -> dict:
    """Return all saved user profiles with their sheet row numbers."""

    try:
        ws = get_worksheet("usersProfile")
        records = ws.get_all_records()
        user_profiles = []

        for index, record in enumerate(records, start=2):
            user_profiles.append(
                {
                    "row_number": index,
                    "user_id": record.get("user_id"),
                    "name": record.get("name", ""),
                    "education": record.get("education", ""),
                    "skills": _json_to_list(record.get("skills", "")),
                    "projects": _json_to_list(record.get("projects", "")),
                    "experience": _json_to_list(record.get("experience", "")),
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
    """Delete a user profile by its Google Sheets row number."""

    try:
        if row_number <= 1:
            return {"status": "error"}

        ws = get_worksheet("usersProfile")
        ws.delete_rows(row_number)

        return {"status": "success"}
    except Exception:
        return {"status": "error"}