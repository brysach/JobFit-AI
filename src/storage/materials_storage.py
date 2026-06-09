# src/storage/materials_storage.py

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
    return get_worksheet("generatedMaterials")


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


def save_generated_materials(materials: dict) -> str:
    """Save generated resume, cover letter, strengths, and weaknesses."""

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
    """Retrieve generated materials by application_id and optional user_id."""

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