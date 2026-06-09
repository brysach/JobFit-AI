# tests/storage/test_materials_storage.py

from __future__ import annotations

from src.storage.materials_storage import get_generated_materials
from src.storage.materials_storage import save_generated_materials


def valid_generated_materials() -> dict:
    return {
        "application_id": 1,
        "user_id": 1,
        "resume_skills": ["Python", "Git"],
        "resume_projects": ["Built JobFit-AI using Python."],
        "resume_experience": ["Tutored students in problem-solving."],
        "cover_letter": "Dear Hiring Team, I am excited to apply.",
        "strengths": ["Strong Python and Git match for the role."],
        "weaknesses": ["Practice React basics before the interview."],
    }


def test_save_generated_materials_success():
    result = save_generated_materials(valid_generated_materials())

    assert result == "success"


def test_save_generated_materials_duplicate_exists():
    materials = valid_generated_materials()

    first_result = save_generated_materials(materials)
    second_result = save_generated_materials(materials)

    assert first_result == "success"
    assert second_result == "exists"


def test_save_generated_materials_missing_required_field_error():
    materials = valid_generated_materials()
    del materials["strengths"]

    result = save_generated_materials(materials)

    assert result == "error"


def test_get_generated_materials_success():
    save_generated_materials(valid_generated_materials())

    result = get_generated_materials(1, user_id=1)

    assert result["status"] == "success"
    assert result["data"]["application_id"] == 1
    assert result["data"]["user_id"] == 1
    assert result["data"]["resume"]["skills"] == ["Python", "Git"]
    assert result["data"]["resume"]["projects"] == ["Built JobFit-AI using Python."]
    assert result["data"]["resume"]["experience"] == [
        "Tutored students in problem-solving."
    ]
    assert result["data"]["cover_letter"] == "Dear Hiring Team, I am excited to apply."
    assert result["data"]["strengths"] == ["Strong Python and Git match for the role."]
    assert result["data"]["weaknesses"] == [
        "Practice React basics before the interview."
    ]


def test_get_generated_materials_not_found():
    result = get_generated_materials(999)

    assert result["status"] == "not_found"
    assert result["message"] == "Generated materials were not found."