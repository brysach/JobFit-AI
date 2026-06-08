# tests/storage/test_user_profile_storage.py

from __future__ import annotations

from src.storage.user_profile_storage import get_user_profile
from src.storage.user_profile_storage import save_user_profile


def valid_user_profile() -> dict:
    return {
        "user_id": 1,
        "name": "Bryan Estrada",
        "education": "B.S. Computer Science, University of California, Riverside",
        "skills": ["Python", "C++", "Git"],
        "projects": ["JobFit-AI", "Minesweeper"],
        "experience": ["Math tutor", "Software engineering project"],
    }


def test_save_user_profile_success():
    result = save_user_profile(valid_user_profile())

    assert result == "success"


def test_save_duplicate_user_profile_exists():
    user_profile = valid_user_profile()

    first_result = save_user_profile(user_profile)
    second_result = save_user_profile(user_profile)

    assert first_result == "success"
    assert second_result == "exists"


def test_missing_required_user_profile_fields_error():
    user_profile = valid_user_profile()
    del user_profile["name"]

    result = save_user_profile(user_profile)

    assert result == "error"


def test_get_user_profile_success():
    user_profile = valid_user_profile()

    save_result = save_user_profile(user_profile)
    get_result = get_user_profile(1)

    assert save_result == "success"
    assert get_result["status"] == "success"
    assert get_result["data"]["user_id"] == 1
    assert get_result["data"]["name"] == "Bryan Estrada"
    assert get_result["data"]["skills"] == ["Python", "C++", "Git"]
    assert get_result["data"]["projects"] == ["JobFit-AI", "Minesweeper"]
    assert get_result["data"]["experience"] == [
        "Math tutor",
        "Software engineering project",
    ]


def test_get_user_profile_not_found():
    result = get_user_profile(999)

    assert result["status"] == "not_found"
    assert result["message"] == "User profile was not found."