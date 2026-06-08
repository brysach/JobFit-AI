# tests/storage/test_materials_storage.py

from __future__ import annotations

from src.storage.materials_storage import get_generated_materials
from src.storage.materials_storage import save_generated_materials


def valid_generated_materials() -> dict:
    return {
        "application_id": 1,
        "user_id": 1,
        "resume_bullets": [
            "Built and tested a Python application using layered architecture.",
            "Integrated Google Sheets storage with structured application data.",
        ],
        "cover_letter": "Dear Hiring Manager, I am excited to apply...",
    }


def test_save_generated_materials_success():
    result = save_generated_materials(valid_generated_materials())

    assert result == "success"


def test_save_duplicate_generated_materials_exists():
    materials = valid_generated_materials()

    first_result = save_generated_materials(materials)
    second_result = save_generated_materials(materials)

    assert first_result == "success"
    assert second_result == "exists"


def test_missing_required_generated_materials_fields_error():
    materials = valid_generated_materials()
    del materials["cover_letter"]

    result = save_generated_materials(materials)

    assert result == "error"


def test_get_generated_materials_success():
    materials = valid_generated_materials()

    save_result = save_generated_materials(materials)
    get_result = get_generated_materials(1)

    assert save_result == "success"
    assert get_result["status"] == "success"
    assert get_result["data"]["application_id"] == 1
    assert get_result["data"]["user_id"] == 1
    assert get_result["data"]["resume_bullets"] == materials["resume_bullets"]
    assert get_result["data"]["cover_letter"] == materials["cover_letter"]


def test_get_generated_materials_not_found():
    result = get_generated_materials(999)

    assert result["status"] == "not_found"
    assert result["message"] == "Generated materials were not found."