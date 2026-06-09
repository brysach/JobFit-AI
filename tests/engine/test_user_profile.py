# tests/engine/test_user_profile.py

from __future__ import annotations

import src.engine.user_profile as user_profile


def valid_user_profile() -> dict:
    return {
        "name": "Bryan Estrada",
        "email": "bryan@example.com",
        "phone_number": "555-123-4567",
        "university": "University of California, Riverside",
        "degree": "B.S. Computer Science",
        "skills": ["Python", "Git"],
        "projects": ["JobFit-AI"],
        "experience": ["Math tutor"],
    }


def test_save_user_profile_success(monkeypatch):
    captured_profile = {}

    def fake_save_user_profile_record(profile: dict) -> dict:
        captured_profile.update(profile)
        return {
            "status": "success",
            "user_id": 1,
        }

    monkeypatch.setattr(
        user_profile,
        "save_user_profile_record",
        fake_save_user_profile_record,
    )

    result = user_profile.save_user_profile(valid_user_profile())

    assert result["status"] == "success"
    assert result["save_status"] == "success"
    assert result["user_id"] == 1
    assert captured_profile["name"] == "Bryan Estrada"
    assert captured_profile["email"] == "bryan@example.com"
    assert captured_profile["university"] == "University of California, Riverside"


def test_save_user_profile_incomplete_missing_email():
    profile = valid_user_profile()
    del profile["email"]

    result = user_profile.save_user_profile(profile)

    assert result["status"] == "incomplete"
    assert result["message"] == "User profile is missing required information."


def test_save_user_profile_incomplete_empty_name():
    profile = valid_user_profile()
    profile["name"] = ""

    result = user_profile.save_user_profile(profile)

    assert result["status"] == "incomplete"


def test_save_user_profile_storage_error(monkeypatch):
    monkeypatch.setattr(
        user_profile,
        "save_user_profile_record",
        lambda profile: {"status": "error"},
    )

    result = user_profile.save_user_profile(valid_user_profile())

    assert result["status"] == "storage_error"
    assert result["message"] == "Could not save user profile."


def test_delete_user_profile_by_index_success(monkeypatch):
    monkeypatch.setattr(
        user_profile,
        "list_user_profile_records",
        lambda: {
            "status": "success",
            "data": [
                {
                    "row_number": 2,
                    "name": "Bryan Estrada",
                }
            ],
        },
    )

    captured_row = {}

    def fake_delete_user_profile_by_row(row_number: int) -> dict:
        captured_row["row_number"] = row_number
        return {
            "status": "success",
            "message": "User profile deleted successfully.",
        }

    monkeypatch.setattr(
        user_profile,
        "delete_user_profile_by_row",
        fake_delete_user_profile_by_row,
    )

    result = user_profile.delete_user_profile_by_index("1")

    assert result["status"] == "success"
    assert captured_row["row_number"] == 2


def test_delete_user_profile_by_index_invalid_selection(monkeypatch):
    monkeypatch.setattr(
        user_profile,
        "list_user_profile_records",
        lambda: {
            "status": "success",
            "data": [],
        },
    )

    result = user_profile.delete_user_profile_by_index("1")

    assert result["status"] == "invalid_selection"
    assert result["message"] == "Please choose a valid entry number."