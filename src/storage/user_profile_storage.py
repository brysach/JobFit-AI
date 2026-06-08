# src/storage/user_profile_storage.py

from __future__ import annotations

import json

from src.storage.google_sheets import get_worksheet


REQUIRED_USER_PROFILE_KEYS = {
    "user_id",
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


def save_user_profile(user_profile: dict) -> str:
    """Save user profile data.

    Return:
    - "success"
    - "exists"
    - "error"
    """

    if not all(key in user_profile for key in REQUIRED_USER_PROFILE_KEYS):
        return "error"

    try:
        ws = get_worksheet("usersProfile")

        existing_ids = ws.col_values(1)
        if str(user_profile["user_id"]) in existing_ids:
            return "exists"

        row = [
            user_profile["user_id"],
            user_profile["name"],
            user_profile["education"],
            _list_to_json(user_profile["skills"]),
            _list_to_json(user_profile["projects"]),
            _list_to_json(user_profile["experience"]),
        ]

        ws.append_row(row)
        return "success"
    except Exception:
        return "error"


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