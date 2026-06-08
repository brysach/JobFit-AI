# src/storage/materials_storage.py

from __future__ import annotations

import json

from src.storage.google_sheets import get_worksheet


REQUIRED_GENERATED_MATERIALS_KEYS = {
    "application_id",
    "user_id",
    "resume_bullets",
    "cover_letter",
}


def _list_to_json(items: list[str]) -> str:
    """Convert a list of strings to a JSON string for Google Sheets."""

    return json.dumps(items)


def _json_to_list(value: object) -> list[str]:
    """Convert a JSON string from Google Sheets back to a list of strings."""

    try:
        data = json.loads(str(value))
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(data, list):
        return []

    return [str(item) for item in data]


def save_generated_materials(materials: dict) -> str:
    """Save generated resume bullets and cover letter.

    Return:
    - "success"
    - "exists"
    - "error"
    """

    if not all(key in materials for key in REQUIRED_GENERATED_MATERIALS_KEYS):
        return "error"

    try:
        ws = get_worksheet("generatedMaterials")

        existing_ids = ws.col_values(1)
        if str(materials["application_id"]) in existing_ids:
            return "exists"

        row = [
            materials["application_id"],
            materials["user_id"],
            _list_to_json(materials["resume_bullets"]),
            materials["cover_letter"],
        ]

        ws.append_row(row)
        return "success"
    except Exception:
        return "error"


def get_generated_materials(application_id: int | str) -> dict:
    """Retrieve generated materials by application_id."""

    try:
        ws = get_worksheet("generatedMaterials")
        records = ws.get_all_records()

        for record in records:
            if str(record.get("application_id")) == str(application_id):
                return {
                    "status": "success",
                    "data": {
                        "application_id": record.get("application_id"),
                        "user_id": record.get("user_id"),
                        "resume_bullets": _json_to_list(
                            record.get("resume_bullets", "")
                        ),
                        "cover_letter": str(record.get("cover_letter", "")),
                    },
                }

        return {
            "status": "not_found",
            "message": "Generated materials were not found.",
        }
    except Exception:
        return {
            "status": "not_found",
            "message": "Generated materials were not found.",
        }