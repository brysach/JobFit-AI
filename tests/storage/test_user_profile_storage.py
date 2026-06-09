# tests/storage/test_user_profile_storage.py

from __future__ import annotations

from src.storage.user_profile_storage import get_user_profile
from src.storage.user_profile_storage import save_user_profile


def valid_user_profile() -> dict:
    return {
        "name": "Bryan Estrada",
        "education": "B.S. Computer Science, University of California, Riverside",
        "skills": ["Python", "C++", "Git"],
        "projects": ["JobFit-AI", "Minesweeper"],
        "experience": ["Math tutor", "Software engineering project"],
    }

def test_save_user_profile_success():
    result = save_user_profile(valid_user_profile())

    assert result["status"] == "success"
    assert result["user_id"] == 1


def test_save_user_profile_generates_incrementing_ids():
    first_result = save_user_profile(valid_user_profile())
    second_result = save_user_profile(valid_user_profile())

    assert first_result["status"] == "success"
    assert second_result["status"] == "success"
    assert first_result["user_id"] == 1
    assert second_result["user_id"] == 2


def test_missing_required_user_profile_fields_error():
    user_profile = valid_user_profile()
    del user_profile["name"]

    result = save_user_profile(user_profile)

    assert result["status"] == "error"


def test_get_user_profile_success():
    save_result = save_user_profile(valid_user_profile())
    user_id = save_result["user_id"]

    get_result = get_user_profile(user_id)

    assert get_result["status"] == "success"
    assert get_result["data"]["user_id"] == user_id
    assert get_result["data"]["name"] == "Bryan Estrada"
    assert get_result["data"]["skills"] == ["Python", "C++", "Git"]


def test_get_user_profile_not_found():
    result = get_user_profile(999)

    assert result["status"] == "not_found"
    assert result["message"] == "User profile was not found."